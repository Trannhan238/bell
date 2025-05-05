from app import db

class WinterShiftConfig(db.Model):
    __tablename__ = 'winter_shift_config'
    __table_args__ = {'extend_existing': True}  # Allow redefining the table if it already exists
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False, unique=True)
    start_month = db.Column(db.Integer, nullable=False, default=10)  # Default to October
    end_month = db.Column(db.Integer, nullable=False, default=3)    # Default to March
    morning_shift_minutes = db.Column(db.Integer, nullable=False, default=0)
    afternoon_shift_minutes = db.Column(db.Integer, nullable=False, default=0)

    # Sửa mối quan hệ để tránh xung đột backref
    school = db.relationship(
        'School', 
        backref=db.backref('winter_shift_from_config', uselist=False),
        overlaps="winter_shift,winter_shift_config,school_winter_shift,school_winter_shift_config"
    )
