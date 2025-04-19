from app import db
from datetime import datetime

class BellProfile(db.Model):
    __tablename__ = "bell_profiles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Ví dụ: "Mùa hè", "Mùa đông"
    active_from = db.Column(db.Date, nullable=False)  # Ngày bắt đầu (mùa hè, mùa đông)
    active_to = db.Column(db.Date, nullable=False)    # Ngày kết thúc

    schedules = db.relationship("Schedule", backref="profile", lazy=True)
