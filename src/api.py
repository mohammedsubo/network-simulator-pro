"""
Enhanced FastAPI Network Simulator with Dashboard Support
Version 2.0.0 - Updated with lifespan handler
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime
import uvicorn
from pathlib import Path
import random

# Data Models
class Device(BaseModel):
    id: str
    type: str  # smartphone, iot, vehicle
    slice: str  # eMBB, URLLC, mMTC
    connected_at: datetime
    latency: float
    throughput: float

class AddDeviceRequest(BaseModel):
    device_type: str
    slice_type: str
    count: int = 1

class NetworkMetrics(BaseModel):
    timestamp: datetime
    network_load: float
    total_devices: int
    avg_latency: float
    throughput: float
    slice_distribution: Dict[str, int]
    devices: List[Dict]

# Global State
class SimulatorState:
    def __init__(self):
        self.devices = {}
        self.metrics_history = []
        self.websocket_clients = []
        self.is_running = False
        self.device_counter = 0
        
    def add_device(self, device_type: str, slice_type: str) -> Device:
        self.device_counter += 1
        device_id = f"{device_type}_{self.device_counter:04d}"
        
        # Latency based on slice type
        latency_ranges = {
            "URLLC": (1, 5),    # Ultra-low latency
            "eMBB": (10, 30),   # Enhanced mobile broadband
            "mMTC": (50, 200)   # Massive IoT
        }
        
        # Throughput based on device type and slice
        throughput_ranges = {
            "smartphone": {"eMBB": (100, 1000), "URLLC": (50, 200), "mMTC": (10, 50)},
            "vehicle": {"eMBB": (50, 500), "URLLC": (100, 500), "mMTC": (20, 100)},
            "iot": {"eMBB": (10, 100), "URLLC": (5, 50), "mMTC": (1, 10)}
        }
        
        device = Device(
            id=device_id,
            type=device_type,
            slice=slice_type,
            connected_at=datetime.now(),
            latency=random.uniform(*latency_ranges.get(slice_type, (10, 50))),
            throughput=random.uniform(*throughput_ranges[device_type][slice_type])
        )
        
        self.devices[device_id] = device
        return device
    
    def remove_device(self, device_id: str) -> bool:
        if device_id in self.devices:
            del self.devices[device_id]
            return True
        return False
    
    def get_metrics(self) -> NetworkMetrics:
        if not self.devices:
            return NetworkMetrics(
                timestamp=datetime.now(),
                network_load=0,
                total_devices=0,
                avg_latency=0,
                throughput=0,
                slice_distribution={"eMBB": 0, "URLLC": 0, "mMTC": 0},
                devices=[]
            )
        
        # Calculate metrics
        total_devices = len(self.devices)
        avg_latency = sum(d.latency for d in self.devices.values()) / total_devices
        total_throughput = sum(d.throughput for d in self.devices.values())
        
        # Network load calculation (simplified)
        max_capacity = 10000  # Mbps
        network_load = min((total_throughput / max_capacity) * 100, 100)
        
        # Slice distribution
        slice_distribution = {"eMBB": 0, "URLLC": 0, "mMTC": 0}
        for device in self.devices.values():
            slice_distribution[device.slice] += 1
        
        # Convert devices to dict
        devices_list = [
            {
                "id": d.id,
                "type": d.type,
                "slice": d.slice,
                "latency": round(d.latency, 2),
                "throughput": round(d.throughput, 2)
            }
            for d in list(self.devices.values())[:20]  # Limit to 20 for performance
        ]
        
        return NetworkMetrics(
            timestamp=datetime.now(),
            network_load=network_load,
            total_devices=total_devices,
            avg_latency=avg_latency,
            throughput=total_throughput,
            slice_distribution=slice_distribution,
            devices=devices_list
        )
    
    def reset(self):
        self.devices.clear()
        self.metrics_history.clear()
        self.device_counter = 0

# Initialize simulator state
simulator = SimulatorState()

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Background Tasks
async def simulate_network():
    """Background task to simulate network activity"""
    while simulator.is_running:
        if simulator.devices:
            # Update device metrics with some randomness
            for device in simulator.devices.values():
                device.latency += random.uniform(-2, 2)
                device.latency = max(1, device.latency)  # Keep positive
                device.throughput += random.uniform(-10, 10)
                device.throughput = max(1, device.throughput)  # Keep positive
            
            # Get current metrics
            metrics = simulator.get_metrics()
            
            # Broadcast to WebSocket clients
            await manager.broadcast({
                "type": "metrics_update",
                "network_load": metrics.network_load,
                "avg_latency": metrics.avg_latency,
                "throughput": metrics.throughput,
                "total_devices": metrics.total_devices,
                "slice_distribution": metrics.slice_distribution
            })
        
        await asyncio.sleep(2)  # Update every 2 seconds

# Lifespan event handler (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    simulator.is_running = True
    
    # Add some initial devices for demo
    for _ in range(5):
        simulator.add_device("smartphone", "eMBB")
    for _ in range(3):
        simulator.add_device("iot", "mMTC")
    for _ in range(2):
        simulator.add_device("vehicle", "URLLC")
    
    # Start background simulation
    simulation_task = asyncio.create_task(simulate_network())
    
    yield
    
    # Shutdown
    simulator.is_running = False
    simulation_task.cancel()
    try:
        await simulation_task
    except asyncio.CancelledError:
        pass

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="5G Network Simulator API",
    description="Advanced 5G Network Simulator with Real-time Monitoring",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if directory exists
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# API Endpoints
@app.get("/")
async def serve_dashboard():
    """Serve the dashboard HTML"""
    dashboard_path = Path('templates/dashboard.html')
    if dashboard_path.exists():
        return FileResponse('templates/dashboard.html')
    else:
        return {"message": "Welcome to 5G Network Simulator API", "docs": "/docs"}

@app.get("/api/status")
async def get_status():
    """Get current simulator status"""
    metrics = simulator.get_metrics()
    return {
        "status": "running" if simulator.is_running else "stopped",
        "total_devices": metrics.total_devices,
        "network_load": round(metrics.network_load, 2),
        "avg_latency": round(metrics.avg_latency, 2),
        "throughput": round(metrics.throughput, 2),
        "slice_distribution": metrics.slice_distribution,
        "devices": metrics.devices
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get current network metrics"""
    metrics = simulator.get_metrics()
    return {
        "timestamp": metrics.timestamp.isoformat(),
        "network_load": round(metrics.network_load, 2),
        "total_devices": metrics.total_devices,
        "avg_latency": round(metrics.avg_latency, 2),
        "throughput": round(metrics.throughput, 2),
        "slice_distribution": metrics.slice_distribution
    }

@app.post("/api/devices")
async def add_devices(request: AddDeviceRequest):
    """Add new devices to the simulation"""
    added_devices = []
    for _ in range(request.count):
        device = simulator.add_device(request.device_type, request.slice_type)
        added_devices.append({
            "id": device.id,
            "type": device.type,
            "slice": device.slice
        })
    
    return {
        "message": f"Added {request.count} device(s)",
        "devices": added_devices
    }

@app.delete("/api/devices/{device_id}")
async def remove_device(device_id: str):
    """Remove a device from the simulation"""
    if simulator.remove_device(device_id):
        return {"message": f"Device {device_id} removed successfully"}
    else:
        raise HTTPException(status_code=404, detail="Device not found")

@app.get("/api/devices")
async def get_devices():
    """Get all connected devices"""
    devices = [
        {
            "id": d.id,
            "type": d.type,
            "slice": d.slice,
            "connected_at": d.connected_at.isoformat(),
            "latency": round(d.latency, 2),
            "throughput": round(d.throughput, 2)
        }
        for d in simulator.devices.values()
    ]
    return {"devices": devices, "count": len(devices)}

@app.post("/api/reset")
async def reset_simulation():
    """Reset the entire simulation"""
    simulator.reset()
    
    # Add some initial devices after reset
    for _ in range(3):
        simulator.add_device("smartphone", "eMBB")
    for _ in range(2):
        simulator.add_device("iot", "mMTC")
    
    return {"message": "Simulation reset successfully"}

@app.post("/api/export")
async def export_metrics():
    """Export current metrics to JSON file"""
    metrics = simulator.get_metrics()
    
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "metrics": {
            "network_load": metrics.network_load,
            "total_devices": metrics.total_devices,
            "avg_latency": metrics.avg_latency,
            "throughput": metrics.throughput,
            "slice_distribution": metrics.slice_distribution
        },
        "devices": metrics.devices
    }
    
    # Save to file
    with open("metrics_export.json", "w") as f:
        json.dump(export_data, f, indent=2)
    
    return {
        "message": "Metrics exported successfully",
        "filename": "metrics_export.json",
        "data": export_data
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "devices_count": len(simulator.devices)
    }

# Info endpoint
@app.get("/info")
async def info():
    """Get API information"""
    return {
        "name": "5G Network Simulator API",
        "version": "2.0.0",
        "description": "Advanced 5G Network Simulator with Real-time Monitoring",
        "endpoints": {
            "dashboard": "/",
            "api_docs": "/docs",
            "api_status": "/api/status",
            "api_metrics": "/api/metrics",
            "api_devices": "/api/devices",
            "websocket": "/ws",
            "health": "/health"
        },
        "features": [
            "Real-time network simulation",
            "WebSocket support",
            "Device management",
            "Metrics export",
            "Interactive dashboard"
        ]
    }

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    host = "0.0.0.0"
    port = 8000
    reload = False
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    # Run the application
    uvicorn.run(
        "api:app" if reload else app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )