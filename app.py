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

model = ColorizationNet()
pretrained = torch.load('model/model-epoch-29-losses-0.009.pth', map_location=torch.device('cpu'))
model.load_state_dict(pretrained)
model.eval()

def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(256),
                                        transforms.CenterCrop(224)])
    image = Image.open(io.BytesIO(image_bytes))
    image = my_transforms(image)
    img_original = np.asarray(image)
    img_original = rgb2gray(img_original)
    img_original = torch.from_numpy(img_original).unsqueeze(0).float()
    return img_original

def recover_image(grayscale_input, ab_input, save_path=None, save_name=None):
    #plt.clf() # clear matplotlib
    # revover image use greyscale image + predicted image in ab space
    color_image = torch.cat((grayscale_input, ab_input), 0).numpy() # combine channels
    color_image = color_image.transpose((1, 2, 0))  # rescale for matplotlib
    color_image[:, :, 0:1] = color_image[:, :, 0:1] * 100
    color_image[:, :, 1:3] = color_image[:, :, 1:3] * 255 - 128
    color_image = lab2rgb(color_image.astype(np.float64))
    return color_image

def get_prediction(image_bytes):
    input_greyscale = transform_image(image_bytes=image_bytes)
    input_greyscale = input_greyscale.unsqueeze(0)
    output_ab = model(input_greyscale)
    print(output_ab.shape, input_greyscale.shape)
    return recover_image(input_greyscale[0].cpu(), output_ab[0].detach().cpu())

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
