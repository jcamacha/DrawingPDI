import asyncio
import base64
import os
import time

import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile, File

from app.core.pdi import session, filters, edges, segmentation
from app.core.pdi.schemas import (
    AnalysisResult,
    ColorDistribution,
    SpecificColors,
    TherapeuticGroups,
    StrokeMetrics,
    SpatialDistribution,
    ColorHistogram,
    ComputationalVAD,
    ChromaticCentroid,
    SemioticMass,
    EnrichedFeatures,
    ProcessedImages,
)

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024


def _validate_extension(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "code": "INVALID_FORMAT",
                "message": "Solo se permiten imágenes JPG y PNG.",
            },
        )
    return ext


def _validate_size(content: bytes) -> None:
    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "code": "EMPTY_FILE",
                "message": "El archivo está vacío.",
            },
        )
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "code": "FILE_TOO_LARGE",
                "message": f"El archivo supera el límite de {MAX_UPLOAD_SIZE_MB}MB.",
            },
        )


@router.post("/images/upload")
async def upload_image(file: UploadFile = File(...)):
    _validate_extension(file.filename or "")

    content = await file.read()
    _validate_size(content)

    image_b64 = base64.b64encode(content).decode("utf-8")
    analysis_id = session.create_session(image_b64)

    import datetime

    return {
        "data": {"analysis_id": analysis_id},
        "meta": {"timestamp": datetime.datetime.now(datetime.UTC).isoformat()},
    }


@router.post("/images/{analysis_id}/analyze")
async def analyze_image(analysis_id: str):
    s = session.get_session(analysis_id)
    if s is None:
        raise HTTPException(
            status_code=404,
            detail={"error": True, "code": "SESSION_NOT_FOUND"},
        )

    img_bytes = base64.b64decode(s.images.original_b64)
    img_array = cv2.imdecode(
        np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR
    )

    start_time = time.monotonic()

    bilateral_arr, canny_arr, color_dist, histogram = await asyncio.gather(
        asyncio.to_thread(filters.apply_bilateral_filter, img_array),
        asyncio.to_thread(edges.apply_canny_edge_detection, img_array),
        asyncio.to_thread(segmentation.compute_color_distribution, img_array),
        asyncio.to_thread(segmentation.compute_color_histogram, img_array),
    )
    stroke_metrics, vad_result, chromatic_mass = await asyncio.gather(
        asyncio.to_thread(edges.compute_stroke_metrics, canny_arr),
        asyncio.to_thread(segmentation.compute_vad_from_histogram, histogram, img_array),
        asyncio.to_thread(segmentation.compute_chromatic_mass, img_array),
    )
    hsv_mask_arr = await asyncio.to_thread(
        segmentation.generate_hsv_mask_visualization, img_array
    )

    elapsed = time.monotonic() - start_time
    if elapsed > 5.0:
        print(
            f"[PERFORMANCE WARNING] analysis_id={analysis_id} tomó {elapsed:.2f}s (> RNF3: 5s)"
        )

    result = AnalysisResult(
        analysis_id=analysis_id,
        timestamp=s.timestamp,
        color_distribution=ColorDistribution(
            specific=SpecificColors(**color_dist["specific"]),
            therapeutic_groups=TherapeuticGroups(
                **color_dist["therapeutic_groups"]
            ),
        ),
        stroke_metrics=StrokeMetrics(
            edge_density_pct=stroke_metrics["edge_density_pct"],
            mean_edge_intensity=stroke_metrics["mean_edge_intensity"],
            stroke_continuity=stroke_metrics["stroke_continuity"],
            fragmentation_ratio=stroke_metrics.get("fragmentation_ratio", 0.0),
            spatial_distribution=SpatialDistribution(
                **stroke_metrics.get("spatial_distribution", {
                    "top_left_pct": 0.0, "top_right_pct": 0.0,
                    "bottom_left_pct": 0.0, "bottom_right_pct": 0.0,
                })
            ),
        ),
        histogram=ColorHistogram(**histogram),
        enriched_features=EnrichedFeatures(
            computational_vad=ComputationalVAD(**vad_result),
            semiotic_mass=SemioticMass(
                dominant_group=chromatic_mass["dominant_group"],
                predominant_color_centroid=ChromaticCentroid(
                    **chromatic_mass["centroid"]
                ),
                quadrant_mass_distribution=SpatialDistribution(
                    **chromatic_mass["quadrant_distribution"]
                ),
            ),
        ),
        detected_symbols=[],
        images=ProcessedImages(
            original_b64=s.images.original_b64,
            filtered_b64=filters.ndarray_to_base64(bilateral_arr),
            canny_b64=filters.ndarray_to_base64(canny_arr),
            hsv_mask_b64=filters.ndarray_to_base64(hsv_mask_arr),
        ),
    )
    session.update_session(analysis_id, result)

    return {
        "data": result.model_dump(),
        "meta": {"elapsed_seconds": round(elapsed, 2)},
    }
