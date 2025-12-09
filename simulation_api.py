"""FastAPI application for turbine simulation management."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(title="Turbine Simulation Manager")

# Serve a small web UI for managing simulations
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/", include_in_schema=False)
async def serve_index() -> FileResponse:
    """Serve the web UI entrypoint."""

    index_path = WEB_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Web UI not found")
    return FileResponse(index_path)


class SimulationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    fst_path: Optional[str] = Field(
        None,
        description="Absolute or relative path to the primary .fst file for the simulation",
    )
    parameters: dict = Field(default_factory=dict, description="Optional simulation settings")


class SimulationCreate(SimulationBase):
    pass


class SimulationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    fst_path: Optional[str] = Field(
        None,
        description="Absolute or relative path to the primary .fst file for the simulation",
    )
    parameters: Optional[dict] = Field(None, description="Optional simulation settings")


class Simulation(SimulationBase):
    id: str


_simulations: Dict[str, Simulation] = {}


def _get_simulation_or_404(simulation_id: str) -> Simulation:
    simulation = _simulations.get(simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation


@app.post("/simulations", response_model=Simulation, status_code=201)
async def create_simulation(payload: SimulationCreate) -> Simulation:
    """Create a new turbine simulation entry."""

    simulation_id = str(uuid4())
    simulation = Simulation(id=simulation_id, **payload.model_dump())
    _simulations[simulation_id] = simulation
    return simulation


@app.get("/simulations", response_model=List[Simulation])
async def list_simulations() -> List[Simulation]:
    """List all known simulations."""

    return list(_simulations.values())


@app.get("/simulations/{simulation_id}", response_model=Simulation)
async def get_simulation(simulation_id: str) -> Simulation:
    """Retrieve an existing simulation by ID."""

    return _get_simulation_or_404(simulation_id)


@app.put("/simulations/{simulation_id}", response_model=Simulation)
async def update_simulation(simulation_id: str, payload: SimulationUpdate) -> Simulation:
    """Modify an existing simulation entry."""

    existing = _get_simulation_or_404(simulation_id)
    update_data = payload.model_dump(exclude_unset=True)
    updated = existing.model_copy(update=update_data)
    _simulations[simulation_id] = updated
    return updated


@app.delete("/simulations/{simulation_id}", status_code=204)
async def delete_simulation(simulation_id: str) -> Response:
    """Delete a simulation entry."""

    _ = _get_simulation_or_404(simulation_id)
    _simulations.pop(simulation_id, None)
    return Response(status_code=204)
