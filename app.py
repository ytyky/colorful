from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import base64

import io
import json

from torchvision import models
import torch
from torchvision import datasets
import torchvision.transforms as transforms
from skimage.color import lab2rgb, rgb2lab, rgb2gray
import numpy as np
from PIL import Image
from flask import Flask, render_template, send_file, request, redirect
from model.model import ColorizationNet, GrayscaleImageFolder

app = Flask(__name__)
app.secret_key = base64.b64encode(os.urandom(24)).decode('utf-8')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return redirect('/')

    return redirect('/home')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def handle_signup():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if user is not None:
        return redirect('/signup')

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return redirect('/home')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/image")
def image():
    return render_template("image.html")

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        img_bytes = file.read()
        image = get_prediction(image_bytes=img_bytes) # np array
        return image

@app.route('/image', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files.get('file')
        if not file:
            return
        img_bytes = file.read()
        img = get_prediction(image_bytes=img_bytes)
        img = Image.fromarray((img*255).astype('uint8'))
        img.save(os.path.join(app.root_path, 'static/result.jpg'))

        return render_template('result.html')
    return render_template('image.html')

if __name__ == "__main__":
    app.run(debug=True)
