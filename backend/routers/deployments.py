import os
import subprocess
from fastapi import APIRouter, HTTPException
from backend.database import get_db_connection
from mlflow.tracking import MlflowClient

router = APIRouter()
client = MlflowClient(tracking_uri="http://localhost:5000")

# Base directory where deployments will be managed
DEPLOYMENT_DIR = "/app/deployments"

# Ensure the deployment directory exists
os.makedirs(DEPLOYMENT_DIR, exist_ok=True)


# List all active deployments
@router.get("/")
def list_deployments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deployments")
    deployments = cursor.fetchall()
    conn.close()

    return [
        {
            "id": dep[0],
            "name": dep[1],
            "model": dep[2],
            "version": dep[3],
            "status": dep[4],
            "last_updated": dep[5]
        }
        for dep in deployments
    ]


# Get deployment details by ID
@router.get("/{deployment_id}")
def get_deployment(deployment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deployments WHERE id = %s", (deployment_id,))
    deployment = cursor.fetchone()
    conn.close()

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return {
        "id": deployment[0],
        "name": deployment[1],
        "model": deployment[2],
        "version": deployment[3],
        "status": deployment[4],
        "last_updated": deployment[5]
    }


# Create a new deployment by pulling the model from MLflow and running it in a Docker container
@router.post("/create")
def create_deployment(name: str, model: str, version: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure model version exists in MLflow
    model_versions = client.search_model_versions(f"name='{model}'")
    model_version_list = [v.version for v in model_versions]

    if version not in model_version_list:
        raise HTTPException(status_code=400, detail="Invalid model version")

    # Get model's download URI from MLflow
    model_uri = f"models:/{model}/{version}"
    local_model_path = os.path.join(DEPLOYMENT_DIR, f"{model}_{version}")

    try:
        client.download_artifacts(run_id=model_versions[0].run_id, path="", dst_path=local_model_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download model artifacts: {str(e)}")

    # Define container name and port
    container_name = f"deployment_{model}_{version}"
    port = 5001  # Change dynamically if needed

    # Run the model inside a Docker container
    docker_run_cmd = f"""
        docker run -d --rm --name {container_name} -p {port}:5001 \
        -v {local_model_path}:/model \
        my-mlflow-serving-image --model-uri /model
    """

    try:
        subprocess.run(docker_run_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to start deployment: {str(e)}")

    # Insert deployment record into the database
    cursor.execute(
        "INSERT INTO deployments (name, model, version, status, last_updated) VALUES (%s, %s, %s, %s, NOW())",
        (name, model, version, "Running")
    )
    conn.commit()
    conn.close()

    return {"message": "Deployment created", "name": name, "model": model, "version": version, "port": port}


# Update deployment status
@router.put("/{deployment_id}/update_status")
def update_deployment_status(deployment_id: int, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE deployments SET status = %s, last_updated = NOW() WHERE id = %s", (status, deployment_id))
    conn.commit()
    conn.close()

    return {"message": f"Deployment {deployment_id} updated to {status}"}


# Stop and delete a deployment
@router.delete("/{deployment_id}")
def delete_deployment(deployment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch deployment details
    cursor.execute("SELECT model, version FROM deployments WHERE id = %s", (deployment_id,))
    deployment = cursor.fetchone()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    model, version = deployment
    container_name = f"deployment_{model}_{version}"

    # Stop the running container
    docker_stop_cmd = f"docker stop {container_name}"
    try:
        subprocess.run(docker_stop_cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to stop deployment container")

    # Remove deployment record from database
    cursor.execute("DELETE FROM deployments WHERE id = %s", (deployment_id,))
    conn.commit()
    conn.close()

    return {"message": f"Deployment {deployment_id} stopped and deleted"}


# Fetch real deployment logs from Docker containers
@router.get("/{deployment_id}/logs")
def get_deployment_logs(deployment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch deployment details
    cursor.execute("SELECT model, version FROM deployments WHERE id = %s", (deployment_id,))
    deployment = cursor.fetchone()
    conn.close()

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    model, version = deployment
    container_name = f"deployment_{model}_{version}"

    # Fetch logs from the running container
    docker_logs_cmd = f"docker logs {container_name} --tail 50"
    try:
        logs = subprocess.check_output(docker_logs_cmd, shell=True, text=True)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to fetch deployment logs")

    return {"deployment_id": deployment_id, "logs": logs.split("\n")}
