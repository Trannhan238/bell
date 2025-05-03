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