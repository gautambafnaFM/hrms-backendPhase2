from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os 
import urllib.parse
from flask_apscheduler import APScheduler

load_dotenv()

app = Flask(__name__)  # local build
CORS(app, origins='*', supports_credentials=True)

DATABASE = "HRMS"
PASSWORD = os.getenv('PASSWORD')
encoded_password = urllib.parse.quote_plus(PASSWORD)    
SERVER = os.getenv('SERVER')
USERNAME = os.getenv('USER_NAME')

# Email configuration
FROM_ADDRESS = os.getenv('EMAIL_FROM_ADDRESS')
FROM_PASSWORD = os.getenv('EMAIL_FROM_PASSWORD')  # Make sure to store your app password here securely
TO_ADDRESS = os.getenv('EMAIL_TO_ADDRESS')

# SQL Server Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     f'mssql+pymssql://{USERNAME}:{encoded_password}@{SERVER}/{DATABASE}'
# )
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mssql+pyodbc://{USERNAME}:{encoded_password}@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SCHEDULER_API_ENABLED '] = True

# Initialize SQLAlchemy once
db = SQLAlchemy(app)

# initialize scheduler
scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

# Don't initialize app in other files, use the `app` object imported here
