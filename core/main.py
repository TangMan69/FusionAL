"""
FusionAL - FastAPI MCP Execution Server

Core execution engine for MCP servers with Docker sandboxing support.
Provides REST APIs for code execution, MCP server registration, and catalog management.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import tempfile
import os
import shutil
from typing import Optional
import sys
import json
from datetime import datetime

try:
    from .runner_docker import run_in_docker
except ImportError:
    try:
        from runner_docker import run_in_docker
    except Exception:
        run_in_docker = None

app = FastAPI(
    title="FusionAL - MCP Execution Server",
    description="AI-powered MCP server builder and executor with Docker sandboxing",
    version="1.0.0"
)


class ExecRequest(BaseModel):
    """Python code execution request."""
    language: str = "python"
    code: str
    timeout: int = 5
    use_docker: Optional[bool] = False
    memory_mb: Optional[int] = 128


@app.post("/execute")
async def execute(req: ExecRequest):
    """Execute Python code with optional Docker sandboxing."""
    if req.language != "python":
        raise HTTPException(
            status_code=400,
            detail="Only 'python' language supported"
        )

    if req.use_docker:
        if run_in_docker is None:
            raise HTTPException(
                status_code=500,
                detail="Docker runner not available on server"
            )
        try:
            result = run_in_docker(
                req.code,
                timeout=req.timeout,
                memory_mb=req.memory_mb
            )
            return result
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=504, detail="Execution timed out")
        except subprocess.CalledProcessError as e:
            return {
                "stdout": e.stdout,
                "stderr": e.stderr,
                "returncode": e.returncode
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Fallback: run locally (NOT sandboxed)
    tmpdir = tempfile.mkdtemp(prefix="fusional-")
    script_path = os.path.join(tmpdir, "script.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(req.code)

    try:
        proc = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=req.timeout
        )
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Execution timed out")
    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "FusionAL MCP Server",
        "timestamp": datetime.utcnow().isoformat()
    }


# MCP Server Registry
REGISTRY = {}
REGISTRY_FILE = os.path.join(os.getcwd(), "mcp_registry.json")


def _load_registry():
    """Load MCP server registry from disk."""
    try:
        if os.path.exists(REGISTRY_FILE):
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                REGISTRY.update(data)
    except Exception:
        pass


def _save_registry():
    """Save MCP server registry to disk."""
    try:
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(REGISTRY, f, indent=2)
    except Exception:
        pass


_load_registry()


class RegisterRequest(BaseModel):
    """MCP server registration request."""
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[dict] = None


@app.post("/register")
async def register(req: RegisterRequest):
    """Register an MCP server in the catalog."""
    if req.name in REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Server '{req.name}' already registered"
        )
    
    REGISTRY[req.name] = {
        "description": req.description,
        "url": req.url,
        "metadata": req.metadata or {},
        "registered_at": datetime.utcnow().isoformat()
    }
    _save_registry()
    
    return {
        "status": "registered",
        "name": req.name,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/catalog")
async def catalog():
    """List all registered MCP servers."""
    return {
        "total": len(REGISTRY),
        "servers": REGISTRY,
        "timestamp": datetime.utcnow().isoformat()
    }
