import sys
import os
from datetime import time  # Import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.schedule import Schedule

def add_sample_schedules():
    app = create_app()
    with app.app_context():
        sample_schedules = [
            {"start_time": time(8, 0), "end_time": time(9, 0), "bell_type": "start_class", "day_of_week": 1, "profile_id": None},
            {"start_time": time(10, 0), "end_time": time(10, 15), "bell_type": "break_time", "day_of_week": 1, "profile_id": None},
            {"start_time": time(12, 0), "end_time": time(13, 0), "bell_type": "end_class", "day_of_week": 1, "profile_id": None},
        ]

        for schedule_data in sample_schedules:
            schedule = Schedule(
                start_time=schedule_data["start_time"],
                end_time=schedule_data["end_time"],  # Added end_time
                bell_type=schedule_data["bell_type"],
                day_of_week=schedule_data["day_of_week"],
                school_id=1,  # Ensure a valid school_id is provided
                profile_id=schedule_data["profile_id"]
            )
            db.session.add(schedule)
        
        db.session.commit()
        print("Sample schedules added.")

if __name__ == "__main__":
    add_sample_schedules()
