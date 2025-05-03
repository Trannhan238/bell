from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="school_user")  # Role: admin, school_admin, school_user
    email = db.Column(db.String(120), unique=True)
    full_name = db.Column(db.String(100))

    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=True)  # School association for school_admin
    school = db.relationship("School", back_populates="users")  # Define the relationship
    devices = db.relationship("Device", back_populates="user")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)