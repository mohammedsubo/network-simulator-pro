from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import asyncio
import sys
import os

# Fix import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import simulator
from src.simulator import NetworkSimulator

# Create FastAPI app
app = FastAPI(title="5G Network Simulator API", version="1.0.0")

# Global simulator instance
simulator = NetworkSimulator()

@app.get("/")
async def root():
    return {"message": "5G Network Simulator API", "status": "running"}

@app.get("/api/status")
async def get_status():
    return simulator.get_network_summary()

@app.post("/api/devices/{device_id}")
async def add_device(device_id: str, device_type: str = "smartphone"):
    result = simulator.add_device(device_id, device_type)
    return {"message": result}

@app.get("/api/slices")
async def get_slices():
    return [s.to_dict() for s in simulator.network_slices.values()]

@app.on_event("startup")
async def startup_event():
    simulator.add_device("default-phone", "smartphone")
    simulator.add_device("default-iot", "sensor")
    asyncio.create_task(simulator.run_simulation(3600))
    print("API Started - Background simulation running")
@app.get("/dashboard")
async def dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Simulator</title>
        <style>
            body { font-family: Arial; background: #1a1a2e; color: #eee; padding: 20px; }
            h1 { color: #16a085; }
            .card { background: #16213e; padding: 15px; margin: 10px; border-radius: 8px; }
            .status { font-size: 20px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>5G Network Simulator</h1>
        <div class="card">
            <h2>Network Status</h2>
            <div id="status">Loading...</div>
        </div>
        <script>
            async function updateStatus() {
                const response = await fetch('/api/status');
                const data = await response.json();
                document.getElementById('status').innerHTML = 
                    `Devices: ${data.total_devices} | Health: ${data.overall_health}`;
            }
            setInterval(updateStatus, 2000);
            updateStatus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
