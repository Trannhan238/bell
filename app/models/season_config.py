from app import db
from datetime import date
from app.models.school import School

class SeasonConfig(db.Model):
    __tablename__ = 'season_config'
    __table_args__ = {'extend_existing': True}  # Allow extending the existing table definition
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)  # Fixed to reference 'schools.id'
    school = db.relationship('School', backref='seasons')
    summer_start = db.Column(db.Date, nullable=False)
    summer_end = db.Column(db.Date, nullable=False)
    winter_start = db.Column(db.Date, nullable=True)  # New field for winter start
    winter_end = db.Column(db.Date, nullable=True)    # New field for winter end

class WinterShiftConfig(db.Model):
    __tablename__ = 'winter_shift_config'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False, unique=True)
    start_month = db.Column(db.Integer, nullable=False, default=10)  # Default to October
    end_month = db.Column(db.Integer, nullable=False, default=3)    # Default to March
    morning_shift_minutes = db.Column(db.Integer, nullable=False, default=0)
    afternoon_shift_minutes = db.Column(db.Integer, nullable=False, default=0)

    school = db.relationship('School', backref=db.backref('winter_shift', uselist=False))