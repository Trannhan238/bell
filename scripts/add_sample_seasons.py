from app import db
from app.models.season_config import SeasonConfig
from datetime import date

def add_sample_seasons():
    sample_seasons = [
        SeasonConfig(
            school_id=1,
            summer_start=date(2025, 6, 1),
            summer_end=date(2025, 8, 31),
            winter_start=date(2025, 12, 1),
            winter_end=date(2026, 2, 28)
        ),
        SeasonConfig(
            school_id=2,
            summer_start=date(2025, 6, 1),
            summer_end=date(2025, 8, 31),
            winter_start=date(2025, 12, 1),
            winter_end=date(2026, 2, 28)
        ),
        SeasonConfig(
            school_id=3,
            summer_start=date(2025, 6, 1),
            summer_end=date(2025, 8, 31),
            winter_start=date(2025, 12, 1),
            winter_end=date(2026, 2, 28)
        )
    ]

    for season in sample_seasons:
        db.session.add(season)

    db.session.commit()
    print("Sample seasons added successfully!")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        add_sample_seasons()