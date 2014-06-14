from flask import Flask, send_from_directory
import config

app = Flask(__name__, static_url_path="")
app.config.from_object("app.config")
from app import views