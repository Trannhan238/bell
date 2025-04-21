from app import db
from datetime import date

class Holiday(db.Model):
    __tablename__ = "holidays"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=True)  # nullable → nghỉ toàn hệ thống
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    school = db.relationship("School", backref="holidays")  # Không xung đột với DisabledPeriod

    @staticmethod
    def is_overlapping(school_id, start_date, end_date, exclude_id=None):
        query = Holiday.query.filter(
            Holiday.school_id == school_id,
            Holiday.start_date <= end_date,
            Holiday.end_date >= start_date
        )
        if exclude_id:
            query = query.filter(Holiday.id != exclude_id)
        return query.first() is not None

class DisabledPeriod(db.Model):  # Định nghĩa DisabledPeriod nếu cần
    __tablename__ = "disabled_periods"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=False)  # Thêm ForeignKey
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    school = db.relationship(
        "School",
        back_populates="disabled_periods"  # Sử dụng back_populates thay vì backref
    )
