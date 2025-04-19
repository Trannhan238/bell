from app import create_app

app = create_app()

with app.app_context():
    print(app.url_map, flush=True)


if __name__ == "__main__":
    app.run(debug=True)
