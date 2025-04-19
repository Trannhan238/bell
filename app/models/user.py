from app import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="school_user")  # admin, school_user
    email = db.Column(db.String(120), unique=True)
    full_name = db.Column(db.String(100))

    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=True)

    devices = db.relationship("Device", backref="user", lazy=True)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)