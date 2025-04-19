from app import db
from datetime import datetime

class DisabledPeriod(db.Model):
    __tablename__ = "disabled_periods"

    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(200), nullable=True)  # Lý do tắt chuông (nghỉ hè, bảo trì,...)

    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=False)
