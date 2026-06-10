from .schemas import AnalysisResult, ProcessedImages
import uuid
import datetime

_sessions: dict[str, AnalysisResult] = {}


def create_session(image_b64: str) -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = AnalysisResult(
        analysis_id=session_id,
        timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
        images=ProcessedImages(original_b64=image_b64),
    )
    return session_id


def get_session(session_id: str) -> AnalysisResult | None:
    return _sessions.get(session_id)


def is_analyzed(session_id: str) -> bool:
    session = _sessions.get(session_id)
    return session is not None and session.color_distribution is not None


def update_session(session_id: str, result: AnalysisResult) -> None:
    _sessions[session_id] = result
