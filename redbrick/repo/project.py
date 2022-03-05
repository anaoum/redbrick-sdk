"""Handlers to access APIs for getting projects."""
import json
from typing import List, Dict, Tuple, Optional
from datetime import datetime

from redbrick.common.client import RBClient
from redbrick.common.project import ProjectRepoInterface
from redbrick.repo.shards import TAXONOMY_SHARD


class ProjectRepo(ProjectRepoInterface):
    """Class to manage interaction with project APIs."""

    def __init__(self, client: RBClient) -> None:
        """Construct ProjectRepo."""
        self.client = client

    def get_project(self, org_id: str, project_id: str) -> Dict:
        """
        Get project name and status.

        Raise an exception if project does not exist.
        """
        query = """
            query sdkGetProjectName($orgId: UUID!, $projectId: UUID!){
                project(orgId: $orgId, projectId: $projectId){
                    orgId
                    projectId
                    name
                    status
                    tdType
                    taxonomy {
                        name
                    }
                    projectUrl
                }
            }
        """
        variables = {"orgId": org_id, "projectId": project_id}
        response: Dict[str, Dict] = self.client.execute_query(query, variables)
        if response.get("project"):
            return response["project"]

        raise Exception("Project does not exist")

    def get_stages(self, org_id: str, project_id: str) -> List[Dict]:
        """Get stages."""
        query = """
            query sdkGetStages($orgId: UUID!, $projectId: UUID!){
                stages(orgId: $orgId, projectId: $projectId){
                    stageName
                    brickName
                    stageConfig
                }
            }
        """
        variables = {"orgId": org_id, "projectId": project_id}
        response: Dict[str, List[Dict]] = self.client.execute_query(query, variables)
        return response["stages"]

    def create_project(
        self, org_id: str, name: str, stages: List[dict], td_type: str, tax_name: str
    ) -> Dict:
        """Create a project and return project_id."""
        query = """
            mutation createProjectSimple(
                $orgId: UUID!
                $name: String!
                $stages: [StageInputSimple!]!
                $tdType: TaskDataType!
                $taxonomyName: String!
                $taxonomyVersion: Int!
            ) {
                createProjectSimple(
                orgId: $orgId
                name: $name
                stages: $stages
                tdType: $tdType
                taxonomyName: $taxonomyName
                taxonomyVersion: $taxonomyVersion
                ) {
                ok
                errors
                project {
                    projectId
                    name
                    desc
                    projectUrl
                }
                stages {
                    stageName
                    brickName
                }
                }
            }
        """
        for stage in stages:
            stage["stageConfig"] = json.dumps(stage["stageConfig"])
        variables = {
            "orgId": org_id,
            "name": name,
            "stages": stages,
            "tdType": td_type,
            "taxonomyName": tax_name,
            "taxonomyVersion": 1,
        }

        response: Dict[str, Dict] = self.client.execute_query(query, variables)
        return {
            "orgId": org_id,
            "projectId": response["createProjectSimple"]["project"]["projectId"],
        }

    def get_org(self, org_id: str) -> Dict:
        """Get organization."""
        query = """
            query getOrgSDK($orgId: UUID!) {
                organization(orgId: $orgId){
                    name
                    orgId
                }
            }
        """
        response: Dict[str, Dict] = self.client.execute_query(query, {"orgId": org_id})
        return response["organization"]

    def get_projects(self, org_id: str) -> List[Dict]:
        """Get all projects in organization."""
        query = """
            query getProjectsSDK($orgId: UUID!) {
                projects(orgId: $orgId) {
                    orgId
                    name
                    projectId
                    status
                    desc
                    projectUrl
                }
            }
        """
        response: Dict[str, List[Dict]] = self.client.execute_query(
            query, {"orgId": org_id}
        )
        return response["projects"]

    def get_taxonomies(self, org_id: str) -> List[Dict]:
        """Get a list of taxonomies."""
        query = f"""
            query getTaxonomiesSDK($orgId: UUID!) {{
                taxonomies(orgId: $orgId) {{
                    {TAXONOMY_SHARD}
                }}
            }}
        """
        response: Dict[str, List[Dict]] = self.client.execute_query(
            query, {"orgId": org_id}
        )
        return response["taxonomies"]

    def delete_project(self, org_id: str, project_id: str) -> None:
        """Delete Project."""
        query = """
            mutation removeProjectSDK($orgId: UUID!, $projectId: UUID!) {
                removeProject(orgId: $orgId, projectId: $projectId) {
                    ok
                }
            }
        """
        self.client.execute_query(query, {"orgId": org_id, "projectId": project_id})

    def get_labeling_information(
        self,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
        first: int,
        cursor: Optional[str] = None,
    ) -> Tuple[List[Dict], Optional[str]]:
        """Get org labeling information."""
        query_string = """
        query firstLabelingTimeSDK(
            $orgId: UUID!
            $startDate: DateTime!
            $endDate: DateTime!
            $first: Int
            $after: String
        ) {
            firstLabelingTime(
                orgId: $orgId
                startDate: $startDate
                endDate: $endDate
                first: $first
                after: $after
            ) {
                entries {
                    project {
                        projectId
                    }
                    taskId
                    user {
                        email
                    }
                    timeSpent
                    date
                }
                cursor
            }
        }
        """
        query_variables = {
            "orgId": org_id,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "first": first,
            "after": cursor,
        }
        result = self.client.execute_query(query_string, query_variables)
        tasks_paged = result.get("firstLabelingTime", {}) or {}
        entries: List[Dict] = tasks_paged.get("entries", []) or []  # type: ignore
        return entries, tasks_paged.get("cursor")
