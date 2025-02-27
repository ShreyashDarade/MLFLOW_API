from fastapi import APIRouter, HTTPException
from backend.mlflow_api import (
    search_registered_models, create_registered_model, get_registered_model,
    update_registered_model, delete_registered_model, rename_registered_model,
    create_model_version, get_model_version, update_model_version, delete_model_version,
    transition_model_version_stage, get_experiment, set_registered_model_tag
)

router = APIRouter()

@router.get("/")
def list_models():
    # Updated to fetch a live list of registered models
    models = search_registered_models()  # Fetch list of registered models
    if isinstance(models, dict) and "error" in models:
        raise HTTPException(status_code=500, detail=models["error"])
    return {"models": models}

@router.post("/create")
def create_model(name: str):
    response = create_registered_model(name)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return response

@router.get("/{name}")
def get_registered_model_route(name: str):
    model = get_registered_model(name)
    if isinstance(model, dict) and "error" in model:
        raise HTTPException(status_code=404, detail=model["error"])
    return {"registered_model": model}

@router.put("/rename/{model_name}")
def rename_model(model_name: str, new_name: str):
    response = rename_registered_model(model_name, new_name)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return response

@router.put("/{name}")
def update_registered_model_route(name: str, description: str):
    model = update_registered_model(name, description)
    if isinstance(model, dict) and "error" in model:
        raise HTTPException(status_code=500, detail=model["error"])
    return {"registered_model": model}

@router.delete("/delete/{model_name}")
def delete_model(model_name: str):
    response = delete_registered_model(model_name)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return response

@router.post("/version/create/{name}")
def create_model_version_route(name: str, run_id: str = "", source: str = "", version: str = ""):
    # If 'version' param is provided (from UI, possibly as run_id), use it as run_id if run_id param is not given
    actual_run_id = run_id or version
    result = create_model_version(name, source, actual_run_id)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return {"model_version": result}

@router.post("/version/update/{name}/{version}")
def update_model_version_route(name: str, version: str, description: str):
    mv = update_model_version(name, version, description)
    if isinstance(mv, dict) and "error" in mv:
        raise HTTPException(status_code=500, detail=mv["error"])
    return {"model_version": mv}

@router.delete("/version/delete/{name}/{version}")
def delete_model_version_route(name: str, version: str):
    response = delete_model_version(name, version)
    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return {"message": "Model version deleted"}

# NEW: Get a specific model version
@router.get("/version/{name}/{version}")
def get_model_version_route(name: str, version: str):
    mv = get_model_version(name, version)
    if isinstance(mv, dict) and "error" in mv:
        raise HTTPException(status_code=404, detail=mv["error"])
    return {"model_version": mv}

@router.post("/set_stage/{name}/{version}")
def transition_model_version_stage_route(name: str, version: str, stage: str):
    mv = transition_model_version_stage(name, version, stage)
    if isinstance(mv, dict) and "error" in mv:
        raise HTTPException(status_code=500, detail=mv["error"])
    return {"model_version": mv}

# NEW: Set a tag for a registered model
@router.post("/{model_name}/set_tag")
def set_model_tag_route(model_name: str, key: str, value: str):
    response = set_registered_model_tag(model_name, key, value)
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return response
