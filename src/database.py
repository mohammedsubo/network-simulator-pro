"""
Database models and operations for Network Simulator
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List, Dict
import json

# Database configuration
DATABASE_URL = "sqlite:///./network_simulator.db"
# For PostgreSQL: "postgresql://user:password@localhost/dbname"

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class DeviceModel(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    device_type = Column(String)  # smartphone, iot, vehicle
    slice_type = Column(String)   # eMBB, URLLC, mMTC
    connected_at = Column(DateTime, default=datetime.now)
    disconnected_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    avg_latency = Column(Float)
    avg_throughput = Column(Float)
    metadata = Column(JSON, nullable=True)

class MetricsHistory(Base):
    __tablename__ = "metrics_history"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    network_load = Column(Float)
    total_devices = Column(Integer)
    avg_latency = Column(Float)
    total_throughput = Column(Float)
    slice_distribution = Column(JSON)
    peak_load = Column(Float)
    
class SimulationSession(Base):
    __tablename__ = "simulation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    started_at = Column(DateTime, default=datetime.now)
    ended_at = Column(DateTime, nullable=True)
    total_devices_connected = Column(Integer, default=0)
    peak_network_load = Column(Float, default=0)
    avg_session_latency = Column(Float, default=0)
    configuration = Column(JSON, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    alert_type = Column(String)  # high_load, device_failure, latency_spike
    severity = Column(String)     # info, warning, critical
    message = Column(String)
    device_id = Column(String, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Database Operations Class
class DatabaseOperations:
    def __init__(self):
        self.session = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    # Device operations
    def add_device(self, device_id: str, device_type: str, slice_type: str, 
                   latency: float, throughput: float) -> DeviceModel:
        """Add a new device to the database"""
        db_device = DeviceModel(
            device_id=device_id,
            device_type=device_type,
            slice_type=slice_type,
            avg_latency=latency,
            avg_throughput=throughput,
            is_active=True,
            metadata={"initial_connection": datetime.now().isoformat()}
        )
        self.session.add(db_device)
        self.session.commit()
        self.session.refresh(db_device)
        return db_device
    
    def remove_device(self, device_id: str) -> bool:
        """Mark device as disconnected"""
        device = self.session.query(DeviceModel).filter(
            DeviceModel.device_id == device_id,
            DeviceModel.is_active == True
        ).first()
        
        if device:
            device.is_active = False
            device.disconnected_at = datetime.now()
            self.session.commit()
            return True
        return False
    
    def get_active_devices(self) -> List[DeviceModel]:
        """Get all active devices"""
        return self.session.query(DeviceModel).filter(
            DeviceModel.is_active == True
        ).all()
    
    def get_device_history(self, device_id: str) -> Optional[DeviceModel]:
        """Get device history"""
        return self.session.query(DeviceModel).filter(
            DeviceModel.device_id == device_id
        ).first()
    
    # Metrics operations
    def save_metrics(self, metrics: Dict) -> MetricsHistory:
        """Save current metrics to history"""
        db_metrics = MetricsHistory(
            network_load=metrics.get('network_load', 0),
            total_devices=metrics.get('total_devices', 0),
            avg_latency=metrics.get('avg_latency', 0),
            total_throughput=metrics.get('throughput', 0),
            slice_distribution=json.dumps(metrics.get('slice_distribution', {})),
            peak_load=metrics.get('network_load', 0)
        )
        self.session.add(db_metrics)
        self.session.commit()
        self.session.refresh(db_metrics)
        return db_metrics
    
    def get_metrics_history(self, hours: int = 24) -> List[MetricsHistory]:
        """Get metrics history for the last N hours"""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return self.session.query(MetricsHistory).filter(
            MetricsHistory.timestamp >= cutoff_time
        ).order_by(MetricsHistory.timestamp.desc()).all()
    
    def get_metrics_summary(self) -> Dict:
        """Get summary statistics"""
        from sqlalchemy import func
        
        # Last 24 hours
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        result = self.session.query(
            func.avg(MetricsHistory.network_load).label('avg_load'),
            func.max(MetricsHistory.network_load).label('max_load'),
            func.min(MetricsHistory.network_load).label('min_load'),
            func.avg(MetricsHistory.avg_latency).label('avg_latency'),
            func.max(MetricsHistory.total_devices).label('max_devices')
        ).filter(MetricsHistory.timestamp >= cutoff_time).first()
        
        return {
            'avg_load': result.avg_load or 0,
            'max_load': result.max_load or 0,
            'min_load': result.min_load or 0,
            'avg_latency': result.avg_latency or 0,
            'max_devices': result.max_devices or 0,
            'time_period': '24 hours'
        }
    
    # Session operations
    def create_session(self, session_id: str, config: Dict = None) -> SimulationSession:
        """Create a new simulation session"""
        db_session = SimulationSession(
            session_id=session_id,
            configuration=json.dumps(config) if config else None
        )
        self.session.add(db_session)
        self.session.commit()
        self.session.refresh(db_session)
        return db_session
    
    def update_session(self, session_id: str, **kwargs):
        """Update session statistics"""
        db_session = self.session.query(SimulationSession).filter(
            SimulationSession.session_id == session_id
        ).first()
        
        if db_session:
            for key, value in kwargs.items():
                if hasattr(db_session, key):
                    setattr(db_session, key, value)
            self.session.commit()
    
    def end_session(self, session_id: str):
        """End a simulation session"""
        db_session = self.session.query(SimulationSession).filter(
            SimulationSession.session_id == session_id
        ).first()
        
        if db_session:
            db_session.ended_at = datetime.now()
            self.session.commit()
    
    # Alert operations
    def create_alert(self, alert_type: str, severity: str, message: str, 
                    device_id: Optional[str] = None) -> Alert:
        """Create a new alert"""
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            device_id=device_id
        )
        self.session.add(alert)
        self.session.commit()
        self.session.refresh(alert)
        return alert
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all unresolved alerts"""
        return self.session.query(Alert).filter(
            Alert.resolved == False
        ).order_by(Alert.timestamp.desc()).all()
    
    def resolve_alert(self, alert_id: int) -> bool:
        """Resolve an alert"""
        alert = self.session.query(Alert).filter(
            Alert.id == alert_id
        ).first()
        
        if alert:
            alert.resolved = True
            alert.resolved_at = datetime.now()
            self.session.commit()
            return True
        return False
    
    # Analytics operations
    def get_device_statistics(self) -> Dict:
        """Get device statistics by type and slice"""
        from sqlalchemy import func
        
        # Device type distribution
        device_types = self.session.query(
            DeviceModel.device_type,
            func.count(DeviceModel.id).label('count')
        ).filter(DeviceModel.is_active == True).group_by(DeviceModel.device_type).all()
        
        # Slice distribution
        slice_types = self.session.query(
            DeviceModel.slice_type,
            func.count(DeviceModel.id).label('count')
        ).filter(DeviceModel.is_active == True).group_by(DeviceModel.slice_type).all()
        
        return {
            'device_types': {dt.device_type: dt.count for dt in device_types},
            'slice_types': {st.slice_type: st.count for st in slice_types},
            'total_active': sum(dt.count for dt in device_types)
        }
    
    def get_performance_trends(self, hours: int = 24) -> List[Dict]:
        """Get performance trends over time"""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        metrics = self.session.query(MetricsHistory).filter(
            MetricsHistory.timestamp >= cutoff_time
        ).order_by(MetricsHistory.timestamp).all()
        
        return [
            {
                'timestamp': m.timestamp.isoformat(),
                'network_load': m.network_load,
                'avg_latency': m.avg_latency,
                'throughput': m.total_throughput,
                'devices': m.total_devices
            }
            for m in metrics
        ]
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data from database"""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Delete old metrics
        self.session.query(MetricsHistory).filter(
            MetricsHistory.timestamp < cutoff_time
        ).delete()
        
        # Delete old resolved alerts
        self.session.query(Alert).filter(
            Alert.resolved == True,
            Alert.resolved_at < cutoff_time
        ).delete()
        
        self.session.commit()

# Helper function to get database session
def get_db():
    db = DatabaseOperations()
    try:
        yield db
    finally:
        db.session.close()

# Initialize database with sample data (optional)
def init_sample_data():
    with DatabaseOperations() as db:
        # Create sample session
        session = db.create_session("sample_session_001", {
            "description": "Initial test session",
            "max_devices": 100
        })
        
        # Add sample devices
        for i in range(5):
            db.add_device(
                f"smartphone_{i:04d}",
                "smartphone",
                "eMBB",
                15.5,
                500.0
            )
        
        # Create sample alert
        db.create_alert(
            "high_load",
            "warning",
            "Network load exceeding 80%"
        )
        
        print("Sample data initialized successfully!")

if __name__ == "__main__":
    # Run this to initialize sample data
    init_sample_data()