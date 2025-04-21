from datetime import date
from app import db

class SeasonConfig(db.Model):
    __tablename__ = 'season_config'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    summer_start = db.Column(db.Date, nullable=False)
    summer_end = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<SeasonConfig(school_id={self.school_id}, summer_start={self.summer_start}, summer_end={self.summer_end})>"
