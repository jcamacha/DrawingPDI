from app.core.pdi.session import create_session, get_session, is_analyzed, update_session
from app.core.pdi.schemas import AnalysisResult, ProcessedImages


def test_create_session_returns_valid_uuid():
    session_id = create_session("fake_base64_data")
    assert len(session_id) == 36
    assert session_id.count("-") == 4


def test_get_session_existing():
    session_id = create_session("fake_base64_data")
    result = get_session(session_id)
    assert result is not None
    assert result.analysis_id == session_id
    assert result.images.original_b64 == "fake_base64_data"


def test_get_session_nonexistent():
    result = get_session("00000000-0000-0000-0000-000000000000")
    assert result is None


def test_is_analyzed_before_analysis():
    session_id = create_session("fake_base64_data")
    assert is_analyzed(session_id) is False
