import pytest
from unittest.mock import MagicMock, patch
from app.services.orchestrator import orchestrator
from app.models.project import Project
from app.models.deployment import Deployment

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@pytest.fixture
def mock_project():
    project = Project(
        id=1,
        name="test-project",
        github_url="https://github.com/test/repo",
        branch="main"
    )
    return project

def test_trigger_deployment_success(mock_db, mock_project):
    with patch("app.services.orchestrator.git_service") as mock_git, \
         patch("app.services.orchestrator.docker_service") as mock_docker, \
         patch("app.services.orchestrator.k8s_service") as mock_k8s:
        
        mock_git.clone_repo.return_value = "/tmp/test-project"
        mock_docker.build_image.return_value = ("test-image:latest", "Build logs...")
        mock_k8s.deploy_project.return_value = True
        
        deployment = orchestrator.trigger_deployment(mock_db, mock_project, "abc12345")
        
        assert deployment.status == "success"
        assert "Cloning repository" in deployment.logs
        assert "--- DOCKER BUILD LOGS ---" in deployment.logs
        assert "Kubernetes deployment/update applied successfully" in deployment.logs
        
        # Verify calls
        mock_git.clone_repo.assert_called_once()
        mock_docker.build_image.assert_called_once()
        mock_k8s.deploy_project.assert_called_once()

def test_trigger_deployment_failure(mock_db, mock_project):
    with patch("app.services.orchestrator.git_service") as mock_git:
        mock_git.clone_repo.side_effect = Exception("Clone failed")
        
        deployment = orchestrator.trigger_deployment(mock_db, mock_project, "abc12345")
        
        assert deployment.status == "failed"
        assert "FATAL ERROR: Clone failed" in deployment.logs

def test_rollback_success(mock_db, mock_project):
    mock_target_deployment = Deployment(
        id=10,
        project_id=1,
        commit_hash="targetcommithash",
        status="success"
    )

    with patch("app.services.orchestrator.k8s_service") as mock_k8s:
        mock_k8s.update_image.return_value = True
        
        deployment = orchestrator.rollback(mock_db, mock_project, mock_target_deployment)
        
        assert deployment.status == "success"
        assert "ROLLBACK-targetc" in deployment.commit_hash
        assert "Successfully patched Kubernetes deployment" in deployment.logs
        mock_k8s.update_image.assert_called_once_with("test-project", "autodeployhub/test-project:targetc")
