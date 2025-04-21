from app import db

class SeasonConfig(db.Model):
    __tablename__ = "season_config"
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    summer_start = db.Column(db.Date, nullable=False)
    summer_end = db.Column(db.Date, nullable=False)