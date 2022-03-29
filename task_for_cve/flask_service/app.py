import os
import torch

import numpy as np
from PIL import Image
import torch.nn as nn
from collections import OrderedDict
from torchvision import models, transforms
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, send_from_directory, jsonify

# Main path. Near will be created directory for save input images
UPLOAD_FOLDER = os.path.abspath('app.py')
# Accepted type of files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# Reference value of image sizes
RESCALE_SIZE = 224
# We need upload model once
NEU_MODEL = []
DEVICE = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
PATH_MODEL = os.path.abspath('model_resnet34_7ep.pt')
DICT_BREEDS = {
    0: 'Australian terrier',
    1: 'Beagle',
    2: 'Border terrier',
    3: 'Dingo',
    4: 'English foxhound',
    5: 'Golden retriever',
    6: 'Old English sheepdog',
    7: 'Rhodesian ridgeback',
    8: 'Samoyed',
    9: 'Shih-Tzu'
}
# Model do prediction long in time and all prediction coast some money
# Such dict can save some
SCORES_DICT = {}

app = Flask(__name__)


def __create_image_directory():
    """
    Create directory for input images if not created
    :return: path for save file
    """
    main_path = "/".join(UPLOAD_FOLDER.split("/")[:-1])
    if not os.path.exists(main_path + "/images"):
        os.mkdir(main_path + "/images")
    return main_path + "/images"


def __download_model(path):
    """
    Download model
    :param path: path to saved model
    :return: nothing
    """
    if not NEU_MODEL:
        NEU_MODEL.append(models.resnet34(pretrained=True))
        NEU_MODEL[0].fc = nn.Sequential(OrderedDict([
            ('batch_norm', nn.BatchNorm1d(512)),
            ('drop1', nn.Dropout(p=0.5)),
            ('linear1', nn.Linear(512, 10))
        ]))
        NEU_MODEL[0].load_state_dict(torch.load(path, map_location=torch.device('cpu')))
        NEU_MODEL[0].eval()
        NEU_MODEL[0].to(DEVICE)


def __count_score(img_path):
    """
    Upload model if not
    :return: prediction
    """
    __download_model(path=PATH_MODEL)
    image = __prepare_data(path=img_path)
    output = NEU_MODEL[0](image.to(DEVICE))
    output = output.cpu()

    # If the difference between the values is less than the threshold, then this indicates that the image does
    # not contain the desired dog breeds. (In this simple way, I'm trying to reduce the likelihood of neural
    # network cheating). The threshold is needed due to the use of the softmax-function.
    np_arr = output.detach().numpy()
    if np.max(np_arr) - np.min(np_arr) <= 410.:
        return {'score': 'Very noisy image. No dog find!'}

    answer = nn.functional.softmax(output.detach(), dim=-1).numpy()
    return DICT_BREEDS[np.argmax(answer)]


def __prepare_data(path):
    """
    Prepare image from input path
    :param path: str - path to image in directory for uploaded images
    :return: tensor
    """
    image = Image.open(path).convert('RGB')
    tfms = transforms.Compose([
        transforms.Resize(RESCALE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    img_tensor = tfms(image).to(DEVICE).unsqueeze(0)
    return img_tensor


def __allowed_file(filename):
    """
    File type checking function
    :param filename: uploaded file name
    :return: is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/example/<filename>', methods=['GET'])
def example(filename):
    main_path = "/".join(UPLOAD_FOLDER.split("/")[:-1]) + '/' + filename
    result = __prepare_data(path=main_path)
    return jsonify(type=result, action='fref')


@app.route('/scores/<filename>', methods=['GET', 'DELETE'])
def scores(filename):
    """
    Return scores for input image or delete it
    :param filename: str
    :return: jsonify-data
    """
    if request.method == 'GET':
        if filename in SCORES_DICT:
            return jsonify(image=filename, score=SCORES_DICT[filename])
        return jsonify(image=filename, score='Score not found')
    elif request.method == 'DELETE':
        if filename in SCORES_DICT:
            del SCORES_DICT[filename]
            return jsonify(image=filename, score='Score was deleted')
        return jsonify(image=filename, score='Score not found')
    return jsonify(image=filename, action='Bad request method')


@app.route('/images/<filename>', methods=['GET', 'DELETE'])
def images(filename):
    """
    Send image back or delete image from service
    :param filename: image name, str
    :return: jsonify
    """
    image_path = __create_image_directory()
    if request.method == 'DELETE':
        main_path = "/".join(UPLOAD_FOLDER.split("/")[:-1])
        if os.path.exists(main_path + '/images/' + filename):
            os.remove(main_path + '/images/' + filename)
            return jsonify(image=filename, action='Deleted')
        return jsonify(image=filename, action='Not found')
    elif request.method == 'GET':
        return send_from_directory(image_path, filename)
    return jsonify(image=filename, action='Bad request method')


@app.route('/classification', methods=('GET', 'POST'))
def classification():
    """
    Download new image and return score
    :return: score or redirect
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and __allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = __create_image_directory()
            file.save(os.path.join(save_path, filename))
            SCORES_DICT[filename] = __count_score(img_path=os.path.join(save_path, filename))
            return jsonify(score=SCORES_DICT[filename])
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
