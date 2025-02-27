from mlflow.tracking import MlflowClient
import mlflow
from mlflow.entities import ViewType

# Tracking server URI
MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
# Ensure MLflow uses the tracking server URI
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

# -------------------------------------
#  📌 Experiments Management
# -------------------------------------
def get_experiments():
    """Retrieve all MLflow experiments"""
    try:
        experiments = client.search_experiments(view_type=ViewType.ALL)
        return [{"id": exp.experiment_id, "name": exp.name, "lifecycle_stage": exp.lifecycle_stage} for exp in experiments]
    except Exception as e:
        return {"error": str(e)}

def get_experiment(experiment_id):
    """Retrieve a specific experiment by ID"""
    try:
        experiment = client.get_experiment(experiment_id)
        return {
            "id": experiment.experiment_id,
            "name": experiment.name,
            "lifecycle_stage": experiment.lifecycle_stage,
            "artifact_location": experiment.artifact_location,
        }
    except Exception as e:
        return {"error": str(e)}

def get_experiment_by_name(name):
    """Retrieve an experiment by its name"""
    try:
        experiment = client.get_experiment_by_name(name)
        if experiment:
            return {
                "id": experiment.experiment_id,
                "name": experiment.name,
                "lifecycle_stage": experiment.lifecycle_stage,
                "artifact_location": experiment.artifact_location,
            }
        else:
            return {"error": "Experiment not found"}
    except Exception as e:
        return {"error": str(e)}

def create_experiment(name):
    """Create a new experiment"""
    try:
        experiment_id = client.create_experiment(name)
        return {"experiment_id": experiment_id}
    except Exception as e:
        return {"error": str(e)}

def update_experiment(experiment_id, new_name):
    """Rename an experiment"""
    try:
        client.rename_experiment(experiment_id, new_name)
        return {"message": "Experiment updated"}
    except Exception as e:
        return {"error": str(e)}

def delete_experiment(experiment_id):
    """Delete an experiment"""
    try:
        client.delete_experiment(experiment_id)
        return {"message": "Experiment deleted"}
    except Exception as e:
        return {"error": str(e)}

def restore_experiment(experiment_id):
    """Restore a deleted experiment"""
    try:
        client.restore_experiment(experiment_id)
        return {"message": "Experiment restored"}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------------
#  📌 Runs Management
# -------------------------------------
def create_run(experiment_id, run_name):
    """Create an MLflow run inside an experiment"""
    try:
        # Ensure experiment exists
        experiment_list = client.search_experiments(view_type=ViewType.ALL)
        experiment_ids = [exp.experiment_id for exp in experiment_list]
        if str(experiment_id) not in [str(eid) for eid in experiment_ids]:
            return {"error": f"Experiment ID {experiment_id} does not exist."}
        # Create the run
        run = client.create_run(experiment_id=str(experiment_id), run_name=run_name)
        # Log an initial parameter
        client.log_param(run.info.run_id, "init_status", "run_started")
        # End the run
        client.set_terminated(run.info.run_id)
        # Fetch the run with all details
        finished_run = client.get_run(run.info.run_id)
        # Prepare run info and data
        info = finished_run.info
        data = finished_run.data
        run_info = {
            "run_id": info.run_id,
            "run_name": info.run_name if hasattr(info, "run_name") else None,
            "experiment_id": info.experiment_id,
            "status": info.status,
            "start_time": info.start_time,
            "end_time": info.end_time,
            "artifact_uri": info.artifact_uri,
            "lifecycle_stage": info.lifecycle_stage
        }
        run_data = {
            "metrics": [{"key": k, "value": v} for k, v in data.metrics.items()] if hasattr(data, "metrics") else [],
            "params": [{"key": k, "value": v} for k, v in data.params.items()] if hasattr(data, "params") else [],
            "tags": [{"key": k, "value": v} for k, v in data.tags.items()] if hasattr(data, "tags") else []
        }
        return {"info": run_info, "data": run_data}
    except Exception as e:
        return {"error": str(e)}

def get_runs(experiment_id):
    """Retrieve all runs for a given experiment"""
    try:
        runs = client.search_runs([experiment_id], run_view_type=ViewType.ACTIVE_ONLY)
        run_list = []
        for run in runs:
            info = run.info
            data = run.data
            run_info = {
                "run_id": info.run_id,
                "run_name": info.run_name if hasattr(info, "run_name") else None,
                "experiment_id": info.experiment_id,
                "status": info.status,
                "start_time": info.start_time,
                "end_time": info.end_time,
                "artifact_uri": info.artifact_uri,
                "lifecycle_stage": info.lifecycle_stage
            }
            run_data = {
                "metrics": [{"key": k, "value": v} for k, v in data.metrics.items()] if hasattr(data, "metrics") else [],
                "params": [{"key": k, "value": v} for k, v in data.params.items()] if hasattr(data, "params") else [],
                "tags": [{"key": k, "value": v} for k, v in data.tags.items()] if hasattr(data, "tags") else []
            }
            run_list.append({"info": run_info, "data": run_data})
        return run_list
    except Exception as e:
        return {"error": str(e)}

def get_run(run_id):
    """Retrieve a specific run by ID"""
    try:
        run = client.get_run(run_id)
        info = run.info
        data = run.data
        run_info = {
            "run_id": info.run_id,
            "run_name": info.run_name if hasattr(info, "run_name") else None,
            "experiment_id": info.experiment_id,
            "status": info.status,
            "start_time": info.start_time,
            "end_time": info.end_time,
            "artifact_uri": info.artifact_uri,
            "lifecycle_stage": info.lifecycle_stage
        }
        run_data = {
            "metrics": [{"key": k, "value": v} for k, v in data.metrics.items()] if hasattr(data, "metrics") else [],
            "params": [{"key": k, "value": v} for k, v in data.params.items()] if hasattr(data, "params") else [],
            "tags": [{"key": k, "value": v} for k, v in data.tags.items()] if hasattr(data, "tags") else []
        }
        return {"info": run_info, "data": run_data}
    except Exception as e:
        return {"error": str(e)}

def delete_run(run_id):
    """Delete a run"""
    try:
        client.delete_run(run_id)
        return {"message": "Run deleted"}
    except Exception as e:
        return {"error": str(e)}

def restore_run(run_id):
    """Restore a deleted run"""
    try:
        client.restore_run(run_id)
        return {"message": "Run restored"}
    except Exception as e:
        return {"error": str(e)}

def log_metric(run_id, key, value):
    try:
        client.log_metric(run_id, key, float(value))
        return {"message": f"Metric {key} logged with value {value}"}
    except Exception as e:
        return {"error": str(e)}

def log_param(run_id, key, value):
    try:
        client.log_param(run_id, key, value)
        return {"message": f"Parameter {key} logged with value {value}"}
    except Exception as e:
        return {"error": str(e)}

def list_artifacts(run_id, path=None):
    """List all artifacts for a given run"""
    try:
        artifacts = client.list_artifacts(run_id, path)
        return [artifact.path for artifact in artifacts]
    except Exception as e:
        return {"error": str(e)}

# -------------------------------------
# NEW: Artifact Management
# -------------------------------------
def log_artifact(run_id, file_path, artifact_path=None):
    """Log an artifact (file) to a specific run"""
    try:
        client.log_artifact(run_id, file_path, artifact_path)
        return {"message": f"Artifact {file_path} logged"}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------------
#  📌 Model Management
# -------------------------------------
def create_registered_model(name):
    """Create a new registered model"""
    try:
        client.create_registered_model(name)
        model = client.get_registered_model(name)
        return {
            "name": model.name,
            "creation_timestamp": model.creation_timestamp,
            "last_updated_timestamp": model.last_updated_timestamp,
            "description": model.description,
            "latest_versions": [
                {
                    "name": mv.name,
                    "version": str(mv.version),
                    "current_stage": mv.current_stage,
                    "creation_timestamp": mv.creation_timestamp,
                    "last_updated_timestamp": mv.last_updated_timestamp,
                    "description": mv.description,
                    "source": mv.source,
                    "run_id": mv.run_id,
                    "status": mv.status,
                    "status_message": mv.status_message
                } for mv in (model.latest_versions or [])
            ]
        }
    except Exception as e:
        return {"error": str(e)}

def get_registered_model(name):
    """Retrieve details of a registered model"""
    try:
        model = client.get_registered_model(name)
        return {
            "name": model.name,
            "creation_timestamp": model.creation_timestamp,
            "last_updated_timestamp": model.last_updated_timestamp,
            "description": model.description,
            "latest_versions": [
                {
                    "name": mv.name,
                    "version": str(mv.version),
                    "current_stage": mv.current_stage,
                    "creation_timestamp": mv.creation_timestamp,
                    "last_updated_timestamp": mv.last_updated_timestamp,
                    "description": mv.description,
                    "source": mv.source,
                    "run_id": mv.run_id,
                    "status": mv.status,
                    "status_message": mv.status_message
                } for mv in (model.latest_versions or [])
            ],
            "tags": [{"key": tag.key, "value": tag.value} for tag in (model.tags or [])]
        }
    except Exception as e:
        return {"error": str(e)}

def rename_registered_model(name, new_name):
    """Rename a registered model"""
    try:
        client.rename_registered_model(name, new_name)
        model = client.get_registered_model(new_name)
        return {
            "name": model.name,
            "creation_timestamp": model.creation_timestamp,
            "last_updated_timestamp": model.last_updated_timestamp,
            "description": model.description,
            "latest_versions": [
                {
                    "name": mv.name,
                    "version": str(mv.version),
                    "current_stage": mv.current_stage,
                    "creation_timestamp": mv.creation_timestamp,
                    "last_updated_timestamp": mv.last_updated_timestamp,
                    "description": mv.description,
                    "source": mv.source,
                    "run_id": mv.run_id,
                    "status": mv.status,
                    "status_message": mv.status_message
                } for mv in (model.latest_versions or [])
            ],
            "tags": [{"key": tag.key, "value": tag.value} for tag in (model.tags or [])]
        }
    except Exception as e:
        return {"error": str(e)}

def update_registered_model(name, description):
    """Update a registered models description"""
    try:
        client.update_registered_model(name=name, description=description)
        model = client.get_registered_model(name)
        return {
            "name": model.name,
            "creation_timestamp": model.creation_timestamp,
            "last_updated_timestamp": model.last_updated_timestamp,
            "description": model.description,
            "latest_versions": [
                {
                    "name": mv.name,
                    "version": str(mv.version),
                    "current_stage": mv.current_stage,
                    "creation_timestamp": mv.creation_timestamp,
                    "last_updated_timestamp": mv.last_updated_timestamp,
                    "description": mv.description,
                    "source": mv.source,
                    "run_id": mv.run_id,
                    "status": mv.status,
                    "status_message": mv.status_message
                } for mv in (model.latest_versions or [])
            ],
            "tags": [{"key": tag.key, "value": tag.value} for tag in (model.tags or [])]
        }
    except Exception as e:
        return {"error": str(e)}

def delete_registered_model(name):
    try:
        client.delete_registered_model(name)
        return {"message": "Model deleted"}
    except Exception as e:
        return {"error": str(e)}

def create_model_version(name, source=None, run_id=None):
    """Create a new model version"""
    try:
        # If source not provided but run_id is given, use run's artifact URI as source
        if (not source or source == "") and run_id:
            run = client.get_run(run_id)
            source = run.info.artifact_uri
        mv = client.create_model_version(name, source, run_id)
        return {
            "name": mv.name,
            "version": str(mv.version),
            "creation_timestamp": mv.creation_timestamp,
            "last_updated_timestamp": mv.last_updated_timestamp,
            "current_stage": mv.current_stage,
            "description": mv.description,
            "source": mv.source,
            "run_id": mv.run_id,
            "status": mv.status,
            "status_message": mv.status_message
        }
    except Exception as e:
        return {"error": str(e)}

def get_model_version(name, version):
    """Retrieve details of a model version"""
    try:
        mv = client.get_model_version(name, version)
        return {
            "name": mv.name,
            "version": str(mv.version),
            "creation_timestamp": mv.creation_timestamp,
            "last_updated_timestamp": mv.last_updated_timestamp,
            "current_stage": mv.current_stage,
            "description": mv.description,
            "source": mv.source,
            "run_id": mv.run_id,
            "status": mv.status,
            "status_message": mv.status_message,
            "tags": [{"key": tag.key, "value": tag.value} for tag in (mv.tags or [])]
        }
    except Exception as e:
        return {"error": str(e)}

def update_model_version(name, version, description):
    """Update a model version"""
    try:
        client.update_model_version(name=name, version=version, description=description)
        mv = client.get_model_version(name, version)
        return {
            "name": mv.name,
            "version": str(mv.version),
            "creation_timestamp": mv.creation_timestamp,
            "last_updated_timestamp": mv.last_updated_timestamp,
            "current_stage": mv.current_stage,
            "description": mv.description,
            "source": mv.source,
            "run_id": mv.run_id,
            "status": mv.status,
            "status_message": mv.status_message
        }
    except Exception as e:
        return {"error": str(e)}

def delete_model_version(name, version):
    """Delete a model version"""
    try:
        client.delete_model_version(name, version)
        return {"message": "Model version deleted"}
    except Exception as e:
        return {"error": str(e)}

def transition_model_version_stage(name, version, stage):
    """Transition a model version to a different stage"""
    try:
        mv = client.transition_model_version_stage(name, version, stage)
        return {
            "name": mv.name,
            "version": str(mv.version),
            "creation_timestamp": mv.creation_timestamp,
            "last_updated_timestamp": mv.last_updated_timestamp,
            "current_stage": mv.current_stage,
            "description": mv.description,
            "source": mv.source,
            "run_id": mv.run_id,
            "status": mv.status,
            "status_message": mv.status_message
        }
    except Exception as e:
        return {"error": str(e)}

def search_registered_models():
    """Search for registered models"""
    try:
        models = client.search_registered_models()
        result = []
        for model in models:
            result.append({
                "name": model.name,
                "creation_timestamp": model.creation_timestamp,
                "last_updated_timestamp": model.last_updated_timestamp,
                "description": model.description,
                "latest_versions": [
                    {
                        "name": mv.name,
                        "version": str(mv.version),
                        "current_stage": mv.current_stage,
                        "creation_timestamp": mv.creation_timestamp,
                        "last_updated_timestamp": mv.last_updated_timestamp,
                        "description": mv.description,
                        "source": mv.source,
                        "run_id": mv.run_id,
                        "status": mv.status,
                        "status_message": mv.status_message
                    } for mv in (model.latest_versions or [])
                ]
            })
        return result
    except Exception as e:
        return {"error": str(e)}

def set_registered_model_tag(name, key, value):
    """Set a tag for a registered model"""
    try:
        client.set_registered_model_tag(name, key, value)
        return {"message": "Model tag set"}
    except Exception as e:
        return {"error": str(e)}
