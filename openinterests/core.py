# shut up useless SA warning:
import warnings; 
warnings.filterwarnings('ignore', 'Unicode type received non-unicode bind param value.')
from sqlalchemy.exc import SAWarning
warnings.filterwarnings('ignore', category=SAWarning)

import logging

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from openinterests import default_settings

logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlaload').setLevel(level=logging.WARN)
logging.getLogger('requests').setLevel(level=logging.WARN)

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('SETTINGS', silent=True)

db = SQLAlchemy(app)

