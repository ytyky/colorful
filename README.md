# Image Colorization

This is a web app that use CNN to recover colored image from black and white.

## Prerequisites

```
pip install -r requirements
```

## Model Architecture

The model used for evaluation is a Convolution Neural Network and the full version is created by [this repo](https://github.com/lukemelas/Automatic-Image-Colorization/) . There are two relative new idea added beyond basic CNN architecture:

(1) It used pretrained model Resnet-18 as backbone
(2) During the data pre-processing phase, the training data is converted from RGB to LAB colorspace (Lightness, A and B). By this mean the separation process is easier and faster.

## Deployment

This app's templates are written in HTML, CSS and Javascript. Additionally, some bootstrap features are also added. It is deployed to AWS EC2 and available at http://54.237.74.181/


## Reference

https://lukemelas.github.io/image-colorization.html

https://pytorch.org/tutorials/intermediate/flask_rest_api_tutorial.html

https://medium.com/techfront/step-by-step-visual-guide-on-deploying-a-flask-application-on-aws-ec2-8e3e8b82c4f7
