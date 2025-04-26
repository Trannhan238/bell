from app import db
from datetime import datetime

class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    ip_address = db.Column(db.String(100))
    mac_address = db.Column(db.String(100), unique=True, index=True)
    
    # Trạng thái thiết bị
    active = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default="unassigned")  # unassigned, assigned
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    
    # Sửa cả hai mối quan hệ để sử dụng back_populates
    school = db.relationship("School", back_populates="devices")
    user = db.relationship("User", back_populates="devices")


