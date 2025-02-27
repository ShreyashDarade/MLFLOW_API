from fastapi import APIRouter, HTTPException
from backend.mlflow_api import (
    get_experiments, get_runs, get_run, create_run, delete_run, restore_run,
    log_metric, log_param, list_artifacts, log_artifact
)

router = APIRouter()

# -------------------------------------
# 📌 List All Runs
# -------------------------------------
@router.get("/")
def list_all_runs():
    """Fetch all runs from all experiments."""
    try:
        experiments = get_experiments()
        if isinstance(experiments, dict) and "error" in experiments:
            raise HTTPException(status_code=500, detail=experiments["error"])
        
        all_runs = []
        for exp in experiments:
            runs = get_runs(exp["id"])
            if isinstance(runs, dict) and "error" in runs:
                raise HTTPException(status_code=500, detail=runs["error"])
            all_runs.extend(runs)
        
        return {"runs": all_runs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------
# 📌 List Runs for Specific Experiment
# -------------------------------------
@router.get("/{experiment_id}")
def list_runs(experiment_id: str):
    """Fetch all runs for a given experiment."""
    runs = get_runs(experiment_id)
    if isinstance(runs, dict) and "error" in runs:
        raise HTTPException(status_code=500, detail=runs["error"])
    return {"runs": runs}

# -------------------------------------
# 📌 Create a Run
# -------------------------------------
@router.post("/create")
def create_run_route(experiment_id: str, run_name: str):
    """Create a new MLflow run."""
    run = create_run(experiment_id, run_name)
    if isinstance(run, dict) and "error" in run:
        raise HTTPException(status_code=500, detail=run["error"])
    # Return the run info and data aligned with MLflow API
    return {"run": run}

# -------------------------------------
# 📌 Get Specific Run by Run ID
# -------------------------------------
@router.get("/run/{run_id}")
def get_run_route(run_id: str):
    """Fetch details of a specific run."""
    run = get_run(run_id)
    if isinstance(run, dict) and "error" in run:
        raise HTTPException(status_code=404, detail=run["error"])
    return {"run": run}

# -------------------------------------
# 📌 Delete Run
# -------------------------------------
@router.delete("/{run_id}")
def delete_run_route(run_id: str):
    """Delete a specific run."""
    response = delete_run(run_id)
    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return {"message": "Run deleted"}

# -------------------------------------
# 📌 Restore Deleted Run
# -------------------------------------
@router.post("/restore/{run_id}")
def restore_run_route(run_id: str):
    """Restore a deleted run."""
    response = restore_run(run_id)
    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return {"message": "Run restored"}

# -------------------------------------
# 📌 Log Metric to Run
# -------------------------------------
@router.post("/{run_id}/log_metric")
def log_metric_route(run_id: str, key: str, value: float):
    response = log_metric(run_id, key, value)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return response

# -------------------------------------
# 📌 Log Parameter to Run
# -------------------------------------
@router.post("/{run_id}/log_param")
def log_param_route(run_id: str, key: str, value: str):
    response = log_param(run_id, key, value)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return response

# -------------------------------------
# 📌 List Artifacts of a Run
# -------------------------------------
@router.get("/artifacts/{run_id}")
def list_artifacts_route(run_id: str):
    """List artifacts for a given run."""
    artifacts = list_artifacts(run_id)
    if isinstance(artifacts, dict) and "error" in artifacts:
        raise HTTPException(status_code=500, detail=artifacts["error"])
    return {"artifacts": artifacts}

# -------------------------------------
# NEW: Log Artifact to Run
# -------------------------------------
@router.post("/{run_id}/log_artifact")
def log_artifact_route(run_id: str, file_path: str, artifact_path: str = None):
    response = log_artifact(run_id, file_path, artifact_path)
    if "error" in response:
         raise HTTPException(status_code=500, detail=response["error"])
    return response
