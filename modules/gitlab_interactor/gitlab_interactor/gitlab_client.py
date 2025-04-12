import os
import gitlab
from gitlab.exceptions import GitlabGetError, GitlabListError, GitlabCreateError

class GitLabClient:
    """
    A class to interact with a GitLab instance.

    Attributes:
        gl (gitlab.Gitlab): The GitLab API client.
    """

    def __init__(self):
        """
        Initialize the GitLabClient.

        Sets up the GitLab API client using environment variables for the GitLab URL and token.
        """
        gitlab_url = os.getenv('GITLAB_URL')
        gitlab_token = os.getenv('GITLAB_TOKEN')
        if not gitlab_url or not gitlab_token:
            raise ValueError("GITLAB_URL and GITLAB_TOKEN environment variables must be set.")
        self.gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)

    def list_repos(self, all_info=False):
        """
        List all repositories accessible to the authenticated user.

        Args:
            all_info (bool): If True, return all possible information for each repository. Defaults to False.

        Returns:
            list: A list of repository dictionaries.
        """
        try:
            projects = self.gl.projects.list(all=True)
        except GitlabListError as e:
            print(f"Error: Failed to list repositories. GitLab API returned an error: {e}")
            return []

        if all_info:
            return [project.attributes for project in projects]
        else:
            return [{"id": project.id, "name": project.name, "web_url": project.web_url} for project in projects]

    def get_repo(self, project_id):
        """
        Get details of a specific repository.

        Args:
            project_id (int): The ID of the project.

        Returns:
            dict: The repository attributes.
        """
        try:
            project = self.gl.projects.get(project_id)
        except GitlabGetError as e:
            print(f"Error: Failed to get repository with ID {project_id}. GitLab API returned an error: {e}")
            return {}

        return project.attributes

    def list_pipelines(self, project_id):
        """
        List all pipelines for a given project.

        Args:
            project_id (int): The ID of the project.

        Returns:
            list: A list of pipeline dictionaries.
        """
        try:
            project = self.gl.projects.get(project_id)
            pipelines = project.pipelines.list()
        except GitlabGetError as e:
            print(f"Error: Failed to get project with ID {project_id} to list pipelines. GitLab API returned an error: {e}")
            return []
        except GitlabListError as e:
            print(f"Error: Failed to list pipelines for project ID {project_id}. GitLab API returned an error: {e}")
            return []

        return [pipeline.attributes for pipeline in pipelines]

    def trigger_pipeline(self, project_id, ref='main'):
        """
        Trigger a pipeline for a given project and branch.

        Args:
            project_id (int): The ID of the project.
            ref (str): The branch or tag to trigger the pipeline on. Defaults to 'main'.

        Returns:
            dict: The triggered pipeline attributes.
        """
        gitlab_token = os.getenv('GITLAB_TOKEN')
        if not gitlab_token:
            print("Error: GITLAB_TOKEN environment variable must be set to trigger a pipeline.")
            return {}

        try:
            project = self.gl.projects.get(project_id)
            pipeline = project.pipelines.create({'ref': ref})
        except GitlabGetError as e:
            print(f"Error: Failed to get project with ID {project_id} to trigger pipeline. GitLab API returned an error: {e}")
            return {}
        except GitlabCreateError as e:
            print(f"Error: Failed to trigger pipeline for project ID {project_id} on ref {ref}. GitLab API returned an error: {e}")
            return {}

        return pipeline.attributes

    def get_pipeline(self, project_id, pipeline_id):
        """
        Get details of a specific pipeline.

        Args:
            project_id (int): The ID of the project.
            pipeline_id (int): The ID of the pipeline.

        Returns:
            dict: The pipeline attributes.
        """
        try:
            project = self.gl.projects.get(project_id)
            pipeline = project.pipelines.get(pipeline_id)
        except GitlabGetError as e:
            print(f"Error: Failed to get pipeline with ID {pipeline_id} for project ID {project_id}. GitLab API returned an error: {e}")
            return {}

        return pipeline.attributes

    def retry_pipeline(self, project_id, pipeline_id):
        """
        Retry the failed builds for a pipeline.

        Args:
            project_id (int): The ID of the project.
            pipeline_id (int): The ID of the pipeline.

        Returns:
            dict: The pipeline attributes after retry.
        """
        try:
            project = self.gl.projects.get(project_id)
            pipeline = project.pipelines.get(pipeline_id)
            pipeline.retry()
        except GitlabGetError as e:
            print(f"Error: Failed to get pipeline with ID {pipeline_id} for project ID {project_id}. GitLab API returned an error: {e}")
            return {}
        except GitlabCreateError as e:
            print(f"Error: Failed to retry pipeline with ID {pipeline_id} for project ID {project_id}. GitLab API returned an error: {e}")
            return {}

        return pipeline.attributes

    def cancel_pipeline(self, project_id, pipeline_id):
        """
        Cancel builds in a pipeline.

        Args:
            project_id (int): The ID of the project.
            pipeline_id (int): The ID of the pipeline.

        Returns:
            dict: The pipeline attributes after cancellation.
        """
        try:
            project = self.gl.projects.get(project_id)
            pipeline = project.pipelines.get(pipeline_id)
            pipeline.cancel()
        except GitlabGetError as e:
            print(f"Error: Failed to get pipeline with ID {pipeline_id} for project ID {project_id}. GitLab API returned an error: {e}")
            return {}
        except GitlabCreateError as e:
            print(f"Error: Failed to cancel pipeline with ID {pipeline_id} for project ID {project_id}. GitLab API returned an error: {e}")
            return {}

        return pipeline.attributes

    def delete_pipeline(self, project_id, pipeline_id):
        """
        Delete a pipeline.

        Args:
            project_id (int): The ID of the project.
            pipeline_id (int): The ID of the pipeline.

        Returns:
            bool: True if the pipeline was deleted successfully, False otherwise.
        """
        try:
            project = self.gl.projects.get(project_id)
            pipeline = project.pipelines.get(pipeline_id)
            pipeline.delete()
        except GitlabGetError as e:
            print(f"Error: Failed to get pipeline with ID {pipeline_id} for project ID {project_id}. GitLab API returned an error: {e}")
            return False
        except GitlabCreateError as e:
            print(f"Error: Failed to delete pipeline with ID {pipeline_id} for project ID {project_id}. GitLab API returned an error: {e}")
            return False

        return True