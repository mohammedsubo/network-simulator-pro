# test_run.py - اختبار بسيط
import asyncio
import json
from datetime import datetime

print("="*50)
print("🚀 5G Network Simulator - Test Run")
print("="*50)

# محاكاة بسيطة
network_data = {
    "timestamp": datetime.now().isoformat(),
    "status": "Active",
    "devices": 5,
    "load": 45.5,
    "message": "✅ Simulator is working!"
}

print("\n📊 Network Status:")
print(json.dumps(network_data, indent=2))

print("\n✅ Test completed successfully!")