# School Bell Frontend

## Overview
This project is a frontend application for managing school bell schedules. It provides an interface for administrators and users to view and manage bell schedules, devices, users, and other related entities.

## How to Run
The application is built using Flask and Jinja2. To run the application, follow these steps:

1. Ensure you have Python installed on your system.
2. Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```
3. Set the `FLASK_APP` environment variable:
   ```bash
   set FLASK_APP=run.py
   ```
4. Run the Flask application:
   ```bash
   flask run
   ```

## Project Structure
- `app/`: Contains the main application code, including models, routes, and utilities.
- `static/`: Contains static files such as CSS and JavaScript.
  - `css/`: Stylesheets for the application.
  - `js/`: JavaScript files for the application.
  - `img/`: Images used in the application.
- `templates/`: Contains HTML templates for the application.
  - `layouts/`: Base layout templates.
  - `pages/`: Specific page templates.
- `scripts/`: Utility scripts for database initialization and other tasks.
- `tests/`: Contains test cases for the application.

## Special Setup
- Ensure that the `venv` directory is set up for a virtual environment to manage dependencies.
- Database migrations are managed using Flask-Migrate. Ensure the database is set up and migrations are applied before running the application.
- Use the `gettoken.bat` script to obtain necessary tokens for authentication if required.

This README provides a basic overview and setup instructions for the School Bell Frontend project. For more detailed information, refer to the documentation or contact the project maintainers.
