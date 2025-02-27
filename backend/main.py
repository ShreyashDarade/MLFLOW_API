from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers with full module path
from backend.routers import experiments, runs, models, deployments

import uvicorn

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(experiments.router, prefix="/experiments", tags=["Experiments"])
app.include_router(runs.router, prefix="/runs", tags=["Runs"])
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(deployments.router, prefix="/deployments", tags=["Deployments"])

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
