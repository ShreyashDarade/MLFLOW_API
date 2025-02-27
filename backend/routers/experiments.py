from fastapi import APIRouter, HTTPException
from backend.mlflow_api import (
    get_experiments, get_experiment, get_experiment_by_name,
    create_experiment, delete_experiment, restore_experiment, update_experiment
)

router = APIRouter()

# -------------------------------------
# 📌 List Experiments
# -------------------------------------
@router.get("/")
def list_experiments():
    """Fetch all MLflow experiments."""
    experiments = get_experiments()
    if isinstance(experiments, dict) and "error" in experiments:
        raise HTTPException(status_code=500, detail=experiments["error"])
    return {"experiments": experiments}

# -------------------------------------
# 📌 Get Experiment by ID
# -------------------------------------
@router.get("/{experiment_id}")
def get_experiment_route(experiment_id: str):
    """Fetch a single experiment by ID."""
    experiment = get_experiment(experiment_id)
    if isinstance(experiment, dict) and "error" in experiment:
        raise HTTPException(status_code=404, detail=experiment["error"])
    return experiment

# -------------------------------------
# 📌 Get Experiment by Name
# -------------------------------------
@router.get("/by_name/{name}")
def get_experiment_by_name_route(name: str):
    """Fetch an experiment by name."""
    experiment = get_experiment_by_name(name)
    if isinstance(experiment, dict) and "error" in experiment:
        raise HTTPException(status_code=404, detail=experiment["error"])
    return experiment

# -------------------------------------
# 📌 Create Experiment
# -------------------------------------
@router.post("/create")
def create_experiment_route(name: str):
    """Create a new MLflow experiment."""
    response = create_experiment(name)
    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return {"message": "Experiment created", "id": response["experiment_id"]}

# -------------------------------------
# 📌 Delete Experiment
# -------------------------------------
@router.delete("/{experiment_id}")
def delete_experiment_route(experiment_id: str):
    """Soft-delete an MLflow experiment."""
    response = delete_experiment(experiment_id)
    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return {"message": "Experiment deleted"}

# -------------------------------------
# 📌 Restore Deleted Experiment
# -------------------------------------
@router.post("/restore/{experiment_id}")
def restore_experiment_route(experiment_id: str):
    """Restore a deleted MLflow experiment."""
    response = restore_experiment(experiment_id)
    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return {"message": "Experiment restored"}

# -------------------------------------
# 📌 Update Experiment Name
# -------------------------------------
@router.put("/{experiment_id}")
def update_experiment_route(experiment_id: str, new_name: str):
    """Rename an existing experiment."""
    response = update_experiment(experiment_id, new_name)
    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return {"message": "Experiment updated"}

@router.get("/debug")
def debug_experiments():
    """Check all available experiments in MLflow."""
    experiments = get_experiments()
    return {"experiments": experiments}
# -------------------------------------