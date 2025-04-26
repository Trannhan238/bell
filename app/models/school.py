from app import db

class School(db.Model):
    __tablename__ = "schools"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))

    users = db.relationship("User", backref="school", lazy=True)
    devices = db.relationship("Device", back_populates="school", lazy=True)
    disabled_periods = db.relationship(
        "DisabledPeriod",
        back_populates="school",
        lazy=True
    )
