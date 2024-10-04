#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Export the Flask app environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the Flask application
flask run --host=0.0.0.0 --reload
