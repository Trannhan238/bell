from app import db
from datetime import time

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)  # Corrected table name for foreign key
    profile_id = db.Column(db.Integer, db.ForeignKey('bell_profiles.id'), nullable=True)
    time_point = db.Column(db.Time, nullable=False)  # Điểm thời gian duy nhất thay vì start/end
    day_of_week = db.Column(db.Integer, nullable=False)  # 0 = Thứ Hai, ..., 6 = Chủ Nhật
    bell_type = db.Column(db.String(50), nullable=False)  # Loại chuông (ví dụ: "vào học", "điểm tiết", "ra chơi", "ra về")
    is_summer = db.Column(db.Boolean, default=False)

    school = db.relationship('School', back_populates='schedules')
    profile = db.relationship('BellProfile', back_populates='schedules')
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, time={self.time_point}, type={self.bell_type})>"
