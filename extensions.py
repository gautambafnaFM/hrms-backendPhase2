from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os 
import urllib.parse

load_dotenv()

app = Flask(__name__)  # local build
CORS(app, origins='*', supports_credentials=True)

DATABASE = "HRMS"
PASSWORD = os.getenv('PASSWORD')
encoded_password = urllib.parse.quote_plus(PASSWORD)    
SERVER = os.getenv('SERVER')
print(SERVER)
USERNAME = os.getenv('USER_NAME')

# SQL Server Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mssql+pymssql://{USERNAME}:{encoded_password}@{SERVER}/{DATABASE}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy once
db = SQLAlchemy(app)

# Don't initialize app in other files, use the `app` object imported here
