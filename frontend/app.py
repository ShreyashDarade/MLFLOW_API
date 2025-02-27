import streamlit as st
import requests
import pandas as pd
import time

API_BASE_URL = "http://localhost:8000"

st.set_page_config(layout="wide", page_title="ML Lifecycle Dashboard")
st.sidebar.title("ML Lifecycle Platform")
selected_tab = st.sidebar.radio("Navigate", ["Experiments", "Runs", "Models", "Model Versions", "Model Stages"])

# -------------------- HELPER FUNCTIONS --------------------
def fetch_data(endpoint):
    """Fetches data from the FastAPI backend and handles errors."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):  # If response is a list, return it directly
                return data
            elif isinstance(data, dict):  # If it's a dictionary, try to return its expected values
                for key in ["experiments", "models", "runs", "versions"]:
                    if key in data:
                        return data[key]
            return data  # Return as is if it's neither list nor expected dictionary
        return []
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

def post_request(endpoint, params):
    """Sends a POST request to the FastAPI backend."""
    response = requests.post(f"{API_BASE_URL}{endpoint}", params=params)
    return response.status_code == 200

def put_request(endpoint, params):
    """Sends a PUT request to the FastAPI backend."""
    response = requests.put(f"{API_BASE_URL}{endpoint}", params=params)
    return response.status_code == 200

def delete_request(endpoint):
    """Sends a DELETE request to the FastAPI backend."""
    response = requests.delete(f"{API_BASE_URL}{endpoint}")
    return response.status_code == 200


# -------------------- EXPERIMENTS --------------------
if selected_tab == "Experiments":
    st.title("Manage Experiments")

    experiments = fetch_data("/experiments/")
    if isinstance(experiments, list) and experiments:
        exp_df = pd.DataFrame(experiments)
        st.dataframe(exp_df, use_container_width=True)
    else:
        st.warning("No experiments found.")

    with st.form("create_experiment"):
        exp_name = st.text_input("New Experiment Name")
        submitted = st.form_submit_button("Create Experiment")
        if submitted and exp_name.strip():
            if post_request("/experiments/create", {"name": exp_name}):
                st.success("Experiment created!")
                time.sleep(1)
                st.rerun()

    # Delete or Restore Experiment
    exp_id = st.text_input("Experiment ID for Delete/Restore")
    col1, col2 = st.columns(2)
    if col1.button("Delete Experiment"):
        delete_request(f"/experiments/{exp_id}")
        st.success("Experiment deleted!")
        time.sleep(1)
        st.rerun()
    if col2.button("Restore Experiment"):
        post_request(f"/experiments/restore/{exp_id}", {})
        st.success("Experiment restored!")
        time.sleep(1)
        st.rerun()

# -------------------- RUNS --------------------
elif selected_tab == "Runs":
    st.title("Manage Runs")
    exp_id = st.text_input("Experiment ID for Runs")
    if exp_id and st.button("Fetch Runs"):
        runs_data = fetch_data(f"/runs/{exp_id}")
        runs = runs_data.get("runs", []) if isinstance(runs_data, dict) else runs_data
        if runs:
            run_df = pd.DataFrame(runs)
            st.dataframe(run_df, use_container_width=True)
        else:
            st.warning("No runs found.")

    with st.form("create_run"):
        run_name = st.text_input("Run Name")
        submitted = st.form_submit_button("Create Run")
        if submitted and exp_id.strip():
            response = requests.post(f"{API_BASE_URL}/runs/create", params={"experiment_id": exp_id, "run_name": run_name})
            if response.status_code == 200:
                run_data = response.json()
                if run_data.get("status") == "FINISHED":
                    st.success(f"Run '{run_name}' created and completed!")
                else:
                    st.warning(f"Run '{run_name}' is still running.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Failed to create run.")

    run_id = st.text_input("Run ID to Log Data")
    log_option = st.radio("Select Log Type", ["Metric", "Parameter"])
    log_key = st.text_input("Log Key (e.g., accuracy, learning_rate)")
    log_value = st.text_input("Log Value (numeric values only)")
    if st.button("Log Data"):
        if log_option == "Metric":
            post_request(f"/runs/{run_id}/log_metric", {"key": log_key, "value": log_value})
            st.success(f"Logged metric: {log_key} = {log_value}")
        elif log_option == "Parameter":
            post_request(f"/runs/{run_id}/log_param", {"key": log_key, "value": log_value})
            st.success(f"Logged parameter: {log_key} = {log_value}")
        st.rerun()

    if st.button("Delete Run"):
        delete_request(f"/runs/{run_id}")
        st.success("Run deleted!")
        st.rerun()

# -------------------- MODELS --------------------
elif selected_tab == "Models":
    st.title("Manage Models")
    models = fetch_data("/models/")
    if models:
        model_df = pd.DataFrame(models)
        st.dataframe(model_df, use_container_width=True)
    else:
        st.warning("No models found.")


    # Create Model
    with st.form("create_model"):
        new_model_name = st.text_input("Model Name")
        submitted = st.form_submit_button("Create Model")
        if submitted and new_model_name.strip():
            if post_request("/models/create", {"name": new_model_name}):
                st.success("Model created!")
                time.sleep(1)
                st.rerun()

    model_name_op = st.text_input("Model Name for Operations")
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("New Model Name")
        if st.button("Rename Model"):
            if put_request(f"/models/rename/{model_name_op}", {"new_name": new_name}):
                st.success("Model renamed!")
                st.rerun()
    with col2:
        if st.button("Delete Model"):
            delete_request(f"/models/delete/{model_name_op}")
            st.success("Model deleted!")
            st.rerun()
            
# -------------------- MODEL VERSIONS --------------------
elif selected_tab == "Model Versions":
    st.title("Manage Model Versions")
    model_name_ver = st.text_input("Model Name for Version")
    version = st.text_input("Model Version")
    run_id_version = st.text_input("Run ID for Model Version (optional)")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Create Model Version"):
            # Endpoint now expects both run_id and version parameters.
            if post_request(f"/models/version/create/{model_name_ver}", {"run_id": run_id_version, "version": version}):
                st.success(f"Model version {version} created for {model_name_ver}")
                st.rerun()
    with col2:
        if st.button("Delete Model Version"):
            # Note the updated endpoint path below.
            delete_request(f"/models/version/delete/{model_name_ver}/{version}")
            st.success(f"Model version {version} deleted!")
            st.rerun()
    with col3:
        if st.button("Get Model Version"):
            mv_data = fetch_data(f"/models/version/{model_name_ver}/{version}")
            if isinstance(mv_data, dict) and "model_version" in mv_data:
                st.write(mv_data["model_version"])
            else:
                st.warning("Model version not found.")

                
                
# -------------------- MODEL STAGES --------------------
elif selected_tab == "Model Stages":
    st.title("Manage Model Stages")
    model_name_stage = st.text_input("Model Name")
    version_stage = st.text_input("Model Version")
    stage = st.selectbox("Select Model Stage", ["Staging", "Production", "Archived"])
    if st.button("Set Model Stage"):
        if post_request(f"/models/set_stage/{model_name_stage}/{version_stage}", {"stage": stage}):
            st.success(f"Model '{model_name_stage}' version '{version_stage}' set to '{stage}'")
            st.rerun()