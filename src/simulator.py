#!/usr/bin/env python3
"""
5G Network Simulator - Simplified Version
A production-ready network simulator with basic functionality
"""

import asyncio
import random
import json
from datetime import datetime
from typing import Dict, List
from enum import Enum

class NetworkStatus(Enum):
    """Network operational states"""
    ACTIVE = "active"
    CONGESTED = "congested"
    DEGRADED = "degraded"

class NetworkSlice:
    """Represents a 5G network slice"""
    def __init__(self, slice_id: str, slice_type: str):
        self.slice_id = slice_id
        self.slice_type = slice_type
        self.current_load = random.randint(20, 60)
        self.status = NetworkStatus.ACTIVE
        self.max_bandwidth = 1000  # Mbps
        self.connected_devices = 0
        
    def update_load(self):
        """Simulate load changes"""
        change = random.randint(-10, 15)
        self.current_load = max(0, min(100, self.current_load + change))
        
        # Update status based on load
        if self.current_load > 80:
            self.status = NetworkStatus.CONGESTED
        elif self.current_load > 60:
            self.status = NetworkStatus.DEGRADED
        else:
            self.status = NetworkStatus.ACTIVE
            
    def get_available_bandwidth(self):
        """Calculate available bandwidth"""
        return self.max_bandwidth * (1 - self.current_load / 100)
        
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "slice_id": self.slice_id,
            "type": self.slice_type,
            "load": self.current_load,
            "status": self.status.value,
            "available_bandwidth": round(self.get_available_bandwidth(), 2),
            "connected_devices": self.connected_devices
        }

class NetworkSimulator:
    """Main network simulator class"""
    def __init__(self):
        self.network_slices = {}
        self.devices = []
        self.metrics_history = []
        self.is_running = False
        self.simulation_time = 0
        
        # Initialize default network slices
        self._initialize_slices()
        
    def _initialize_slices(self):
        """Create default network slices"""
        slices_config = [
            ("EMBB-001", "Enhanced Mobile Broadband"),
            ("URLLC-001", "Ultra Reliable Low Latency"),
            ("MMTC-001", "Massive Machine Type")
        ]
        
        for slice_id, slice_type in slices_config:
            self.network_slices[slice_id] = NetworkSlice(slice_id, slice_type)
            
        print(f"Initialized {len(self.network_slices)} network slices")
        
    def add_device(self, device_id: str, device_type: str):
        """Add a device to the network"""
        device = {
            "id": device_id,
            "type": device_type,
            "connected_at": datetime.now().isoformat(),
            "data_usage": 0
        }
        self.devices.append(device)
        
        # Assign to a random slice
        slice = random.choice(list(self.network_slices.values()))
        slice.connected_devices += 1
        
        return f"Device {device_id} added to slice {slice.slice_id}"
        
    def get_network_summary(self):
        """Get current network status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "simulation_time": self.simulation_time,
            "total_devices": len(self.devices),
            "network_slices": [s.to_dict() for s in self.network_slices.values()],
            "overall_health": self._calculate_health()
        }
        
    def _calculate_health(self):
        """Calculate overall network health"""
        congested = sum(1 for s in self.network_slices.values() 
                       if s.status == NetworkStatus.CONGESTED)
        
        if congested == 0:
            return "healthy"
        elif congested == 1:
            return "degraded"
        else:
            return "critical"
            
    async def simulate_network_conditions(self):
        """Simulate changing network conditions"""
        while self.is_running:
            # Update each slice
            for slice in self.network_slices.values():
                slice.update_load()
                
            # Record metrics
            self.metrics_history.append({
                "time": self.simulation_time,
                "timestamp": datetime.now().isoformat(),
                "slices": {s.slice_id: s.current_load 
                          for s in self.network_slices.values()}
            })
            
            # Keep only last 100 metrics
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
                
            self.simulation_time += 1
            await asyncio.sleep(1)
            
    async def run_simulation(self, duration_seconds: int = 30):
        """Run the simulation for specified duration"""
        self.is_running = True
        print(f"Starting simulation for {duration_seconds} seconds...")
        
        # Start background task
        simulation_task = asyncio.create_task(self.simulate_network_conditions())
        
        # Wait for duration
        await asyncio.sleep(duration_seconds)
        
        # Stop simulation
        self.is_running = False
        simulation_task.cancel()
        
        try:
            await simulation_task
        except asyncio.CancelledError:
            pass
            
        print("Simulation completed!")
        
    def export_metrics(self, filename: str = "metrics.json"):
        """Export metrics to JSON file"""
        with open(filename, 'w') as f:
            json.dump({
                "simulation_data": self.metrics_history,
                "final_state": self.get_network_summary()
            }, f, indent=2)
        print(f"Metrics exported to {filename}")

# Demo function
async def main():
    """Demo the simulator"""
    print("="*60)
    print("5G Network Simulator - Starting")
    print("="*60)
    
    # Create simulator
    sim = NetworkSimulator()
    
    # Add some devices
    devices = [
        ("phone-001", "smartphone"),
        ("phone-002", "smartphone"),
        ("laptop-001", "laptop"),
        ("iot-001", "sensor"),
        ("iot-002", "sensor")
    ]
    
    for device_id, device_type in devices:
        result = sim.add_device(device_id, device_type)
        print(f"  {result}")
    
    # Show initial state
    print("\nInitial Network State:")
    summary = sim.get_network_summary()
    print(json.dumps(summary, indent=2))
    
    # Run simulation
    print("\nRunning simulation...")
    await sim.run_simulation(duration_seconds=10)
    
    # Show final state
    print("\nFinal Network State:")
    summary = sim.get_network_summary()
    print(json.dumps(summary, indent=2))
    
    # Export metrics
    sim.export_metrics()
    
    print("\n" + "="*60)
    print("Simulation Complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())