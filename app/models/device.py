from app import db

class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    ip_address = db.Column(db.String(100))
    mac_address = db.Column(db.String(100))

    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
