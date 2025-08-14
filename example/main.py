import requests
import numpy as np
from flask import Flask
import nothingishere

import torch
import torchaudio
import torchvision

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run()