from app import db
from sqlalchemy.sql import text

def inspect_season_config():
    query = text("SELECT name FROM sqlite_master WHERE type='table' AND name='season_config';")
    result = db.session.execute(query).fetchall()
    if result:
        print("Table 'season_config' exists.")
    else:
        print("Table 'season_config' does not exist.")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        inspect_season_config()