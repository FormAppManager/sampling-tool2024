from dataclasses import dataclass
from threading import Thread
from flask import Flask, render_template, Response, request, send_from_directory, session, send_file, jsonify
from werkzeug.utils import secure_filename
from videoAnalyzer import VideoAnalyzer
from src.trackables.areaObject import Roi
import numpy as np
import os
from scipy import stats
import json
import requests
from jose import jwt


UPLOAD_FOLDER = 'src/static/'

app = Flask(__name__, static_folder='src/static')
app.jinja_env.auto_reload = True
#app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




def checkToken(token):
    try:
        target_audience = "formsappdb"
        response = requests.get("https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com")
        certs = json.loads(response.text)
        user = jwt.decode(token, certs, algorithms='RS256', audience=target_audience)
        return user
    except Exception as e:
        return False


@app.route('/home/<token>')
def index(token):
    if checkToken(token):
        return render_template('uploadVideo.html', show_drawer=False, usToken=token)
    return False

@app.route('/image')
def image():
    return send_file(os.path.join('static', 'frame-0.jpg'),  mimetype='image/jpeg')

@app.route('/videofile', methods = ['GET'])
def video_file():
    try:
        file = open(os.path.sep.join(["src", "static", "out.avi",]), "rb")
        mimetype = "multipart/x-mixed-replace"
        headers = {"Content-disposition":"attachment; filename=out.avi"}
        return Response( file, mimetype, headers)
    except FileNotFoundError:
        print("---- NOT FOUND FILE!")

@app.route('/csv', methods = ['GET'])
def csv_file():
    try:
        file = open(os.path.sep.join(["src", "static", "timeResponses.csv",]), "rb")
        mimetype="text/csv"
        headers = {"Content-disposition":"attachment; filename=timesResponse.csv"}
        return Response( file, mimetype, headers)
    except FileNotFoundError:
        print("---- NOT FOUND FILE!")


def do_Analisis(name, user, points, filename):
    roiArea = Roi(points)
    roiArea.changeFormat()

    newDetector = VideoAnalyzer(os.path.join(app.config['UPLOAD_FOLDER'], filename), roiArea)
    checks = newDetector.analyze()
    data = {
        "data":{
            'name': name,
            'checks': checks,
        },
        "mail": user['email'],
        "ref":user['user_id']
    }
    requests.post("https://formsappdb.uc.r.appspot.com/api/video/saveData", json=data)
    # response = requests.post("http://192.168.0.5:8080/api/video/saveData", json=data)

    os.remove(app.config['UPLOAD_FOLDER']+filename)

@app.route('/home/uploadVideo', methods = ['POST'])
def upload_file():
    if request.method == 'POST':
        token = request.form['token']
        user = checkToken(token)
        if user==False:
            return 'Session expired'
        file = request.files['file']
        name = request.form['name']
        points = request.form['coordinates']
        show_drawer = False
        email = 'example@gmail.com'
        if file.filename != '' and points != '' and name != '':
            email = user['email']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            thread = Thread(target=do_Analisis, kwargs={'name': name, 'user': user, 'points':points, 'filename': filename})  # start the thread
            thread.start()
            show_drawer = True
        return render_template('uploadVideo.html', show_drawer=show_drawer, usToken=token, usEmail = email )

def doStats(data):
    return np.mean(data)

def doIsolatedStats(data):
    return {
        'range': str(round(np.amax(data)-np.amin(data), 4)),
        'max': str(round(np.amax(data), 4)),
        'min': str(round(np.amin(data), 4)),
        'len': str(round(np.size(data), 4)),
        'mean': str(round(np.mean(data), 4)),
        'median': str(round(np.median(data), 4)),
        'stdev': str(round(np.std(data), 4)),
    }


@app.route('/getDataStats', methods = ['POST'])
def sampStats():
    data = request.json
    if len(data) == 0:
        return jsonify({})
    elif len(data) == 1:
        data = doIsolatedStats(np.array(data[0]))
    elif len(data) > 1:
        data = doIsolatedStats(np.array(list(map(doStats, data))))
    return jsonify(data)


if __name__ == '__main__':
    # defining server ip address and port
    app.run(host='0.0.0.0',port='5000', debug=True, use_reloader=True)