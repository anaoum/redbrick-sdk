"""
Tests for `redbrick.export.public.ExportRepo`.
These tests are to ensure data gotten from the API is properly parsed.
"""
from unittest.mock import Mock, patch, AsyncMock

import aiohttp
import pytest

from tests.test_repo import conftest as repo_conftest


@pytest.mark.unit
def test_datapoints_in_project(mock_export_repo):
    """Test `redbrick.repo.export.Export.datapoints_in_project`"""
    mock_query = Mock(return_value=repo_conftest.datapoints_in_project_resp)
    with patch.object(mock_export_repo.client, "execute_query", mock_query):
        resp = mock_export_repo.datapoints_in_project(org_id="mock", project_id="mock")
    assert isinstance(resp, int)
    assert resp == 7


@pytest.mark.unit
def test_get_datapoint_latest(mock_export_repo):
    """Test `redbrick.repo.export.Export.get_datapoint_latest`"""
    mock_task_id = "mock_task_id"
    mock_query = Mock(
        return_value=repo_conftest.get_datapoint_latest_resp(mock_task_id)
    )
    with patch.object(mock_export_repo.client, "execute_query", mock_query):
        resp = mock_export_repo.get_datapoint_latest(
            org_id="mock", project_id="mock", task_id=mock_task_id
        )
    assert isinstance(resp, dict)
    assert resp.get("taskId") == mock_task_id
    assert resp.get("dpId") is not None


@pytest.mark.unit
def test_get_datapoints_latest(mock_export_repo):
    """Test `redbrick.repo.export.Export.get_datapoints_latest`"""
    mock_query = Mock(return_value=repo_conftest.get_datapoints_latest_resp)
    with patch.object(mock_export_repo.client, "execute_query", mock_query):
        resp = mock_export_repo.get_datapoints_latest(org_id="mock", project_id="mock")

    assert isinstance(resp, tuple)
    assert len(resp) == 3

    entries, _, _ = resp
    assert isinstance(entries, list)
    assert len(entries) == 7

    task_ids = [x.get("taskId") for x in entries]
    dp_ids = [x.get("dpId") for x in entries]
    assert all(isinstance(x, str) for x in task_ids)
    assert all(isinstance(x, str) for x in dp_ids)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_labels(mock_export_repo):
    """Test `redbrick.repo.export.Export.get_labels`"""
    mock_dp_id = "mock_dp_id"
    mock_label_data = {"dpId": mock_dp_id, "random_bool": True}
    mock_query = AsyncMock(return_value=repo_conftest.get_labels_resp(mock_label_data))
    with patch.object(mock_export_repo.client, "execute_query_async", mock_query):
        async with aiohttp.ClientSession() as aio_session:
            resp = await mock_export_repo.get_labels(
                session=aio_session, org_id="mock", project_id="mock", dp_id=mock_dp_id
            )
    assert isinstance(resp, dict)
    assert resp == mock_label_data


@pytest.mark.unit
def test_task_search(mock_export_repo):
    """Test `redbrick.repo.export.Export.task_search`"""
    mock_stage_name = "Review_1"
    mock_query = Mock(return_value=repo_conftest.task_search_resp(mock_stage_name))
    with patch.object(mock_export_repo.client, "execute_query", mock_query):
        resp = mock_export_repo.task_search(
            org_id="mock", project_id="mock", stage_name=mock_stage_name
        )
    assert isinstance(resp, tuple)
    assert len(resp) == 2

    entries, _ = resp
    assert isinstance(entries, list)
    assert len(entries) == 1
    assert isinstance(entries[0].get("taskId"), str)
    assert entries[0].get("currentStageName") == mock_stage_name


@pytest.mark.unit
def test_presign_items(mock_export_repo):
    """Test `redbrick.repo.export.Export.presign_items`"""
    mock_query = Mock(return_value=repo_conftest.presign_items_resp)
    with patch.object(mock_export_repo.client, "execute_query", mock_query):
        resp = mock_export_repo.presign_items(
            org_id="mock", storage_id="mock", items=[]
        )
    assert isinstance(resp, list)
    assert len(resp) == 1


@pytest.mark.unit
def test_task_events(mock_export_repo):
    """Test `redbrick.repo.export.Export.task_events`"""
    mock_stage_name = "Review_1"
    mock_query = Mock(return_value=repo_conftest.task_events_resp)
    with patch.object(mock_export_repo.client, "execute_query", mock_query):
        resp = mock_export_repo.task_events(
            org_id="mock", project_id="mock", stage_name=mock_stage_name
        )
    assert isinstance(resp, tuple)
    assert len(resp) == 2

    entries, _ = resp
    assert isinstance(entries, list)
    assert len(entries) == 2
    assert isinstance(entries[0], dict)
    assert isinstance(entries[0].get("genericEvents"), list)


@pytest.mark.unit
def test_active_time(mock_export_repo):
    """Test `redbrick.repo.export.Export.active_time`"""
    mock_stage_name = "Label"
    mock_task_id = "mock_task_id"
    mock_query = Mock(return_value=repo_conftest.active_time_resp(mock_task_id))
    with patch.object(mock_export_repo.client, "execute_query", mock_query):
        resp = mock_export_repo.active_time(
            org_id="mock",
            project_id="mock",
            stage_name=mock_stage_name,
            task_id=mock_task_id,
        )
    assert isinstance(resp, tuple)
    assert len(resp) == 2

    entries, _ = resp
    assert isinstance(entries, list)
    assert len(entries) == 1
    assert isinstance(entries[0], dict)
    assert entries[0].get("taskId") == mock_task_id
