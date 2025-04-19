from app import db
from datetime import time

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('bell_profiles.id'), nullable=True)  # Add ForeignKey to BellProfile
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0 = Monday, ..., 6 = Sunday
    bell_type = db.Column(db.String(50))  # Type of bell (e.g., "start", "end")
    is_summer = db.Column(db.Boolean, default=False)

    school = db.relationship('School', backref=db.backref('schedules', lazy=True))
    profile = db.relationship('BellProfile', back_populates='schedules')  # Define relationship with BellProfile
