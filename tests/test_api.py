"""API endpoint tests."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "version" in data


def test_create_dataset(client: TestClient, sample_dataset_data):
    """Test dataset creation."""
    response = client.post("/api/v1/datasets/", json=sample_dataset_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == sample_dataset_data["name"]
    assert data["owner"] == sample_dataset_data["owner"]
    assert "id" in data


def test_list_datasets(client: TestClient, sample_dataset_data):
    """Test dataset listing."""
    # Create a dataset first
    client.post("/api/v1/datasets/", json=sample_dataset_data)

    # List datasets
    response = client.get("/api/v1/datasets/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_dataset(client: TestClient, sample_dataset_data):
    """Test getting a specific dataset."""
    # Create a dataset first
    create_response = client.post("/api/v1/datasets/", json=sample_dataset_data)
    dataset_id = create_response.json()["id"]

    # Get the dataset
    response = client.get(f"/api/v1/datasets/{dataset_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == dataset_id
    assert data["name"] == sample_dataset_data["name"]


def test_create_anomaly(client: TestClient, sample_anomaly_data):
    """Test anomaly creation."""
    # Create a dataset first
    dataset_data = {"name": "test_events", "owner": "test_user"}
    client.post("/api/v1/datasets/", json=dataset_data)

    # Create an anomaly
    response = client.post("/api/v1/anomalies/", json=sample_anomaly_data)
    assert response.status_code == 201

    data = response.json()
    assert data["issue_type"] == sample_anomaly_data["issue_type"]
    assert data["severity"] == sample_anomaly_data["severity"]
    assert "id" in data


def test_list_anomalies(client: TestClient, sample_anomaly_data):
    """Test anomaly listing."""
    # Create a dataset and anomaly first
    dataset_data = {"name": "test_events", "owner": "test_user"}
    client.post("/api/v1/datasets/", json=dataset_data)
    client.post("/api/v1/anomalies/", json=sample_anomaly_data)

    # List anomalies
    response = client.get("/api/v1/anomalies/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_create_run(client: TestClient):
    """Test run creation."""
    # Create a dataset first
    dataset_data = {"name": "test_events", "owner": "test_user"}
    create_response = client.post("/api/v1/datasets/", json=dataset_data)
    dataset_id = create_response.json()["id"]

    # Create a run
    run_data = {"dataset_id": dataset_id, "status": "pending"}
    response = client.post("/api/v1/runs/", json=run_data)
    assert response.status_code == 201

    data = response.json()
    assert data["dataset_id"] == dataset_id
    assert data["status"] == "pending"
    assert "id" in data


def test_agent_workflow_trigger(client: TestClient):
    """Test agent workflow triggering."""
    # Create a dataset first
    dataset_data = {"name": "test_events", "owner": "test_user"}
    create_response = client.post("/api/v1/datasets/", json=dataset_data)
    dataset_id = create_response.json()["id"]

    # Trigger workflow
    workflow_data = {"dataset_id": dataset_id, "include_llm_explanation": True}
    response = client.post("/api/v1/agent/workflow", json=workflow_data)
    assert response.status_code == 200

    data = response.json()
    assert "run_id" in data
    assert data["status"] == "pending"
    assert "message" in data
