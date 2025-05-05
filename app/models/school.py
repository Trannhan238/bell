from app import db

class School(db.Model):
    __tablename__ = "schools"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))

    users = db.relationship("User", back_populates="school", lazy="dynamic")
    devices = db.relationship("Device", back_populates="school", lazy=True)
    disabled_periods = db.relationship(
        "DisabledPeriod",
        back_populates="school",
        lazy=True
    )
    schedules = db.relationship("Schedule", back_populates="school", lazy=True)
    
    # Thêm mối quan hệ rõ ràng với tham số overlaps để tắt cảnh báo
    winter_shift = db.relationship(
        "app.models.winter_shift_config.WinterShiftConfig",
        backref="school_winter_shift",
        uselist=False,
        overlaps="winter_shift_config,school"
    )
    winter_shift_config = db.relationship(
        "app.models.winter_shift_config.WinterShiftConfig",
        backref="school_winter_shift_config",
        uselist=False,
        overlaps="school_winter_shift"
    )
