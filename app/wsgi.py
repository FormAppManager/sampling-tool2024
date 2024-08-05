# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template,request
from videoAnalyzer import VideoAnalyzer
import json
from src.trackables.areaObject import Roi
import numpy as np
from videoAnalyzerCinta import VideoAnalyzerCinta
from flask import Flask, request, render_template
import os
import numpy as np
import pandas as pd
from ultralytics import YOLO
app = Flask(__name__)
def parse_roi_area(coordinates_str):
    try:
        coordinates_list = json.loads(coordinates_str)
        return coordinates_list
    except json.JSONDecodeError:
        return None
@app.route('/')
def about():
    return render_template('home.html')
@app.route('/ipCamera')
def ipcam():
    return render_template('ipCam.html')
@app.route('/manualTimer')
def manual():
    return render_template('manualTimer.html')
@app.route('/uploadVideo', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('uploadVideo.html')
    elif request.method == 'POST':
        if 'file' not in request.files:
            return 'No se ha enviado ningun archivo de video'
        
        # Obteniendo el archivo de video del formulario
        file = request.files['file']
        # Verifica si el usuario no seleccion� ning�n archivo
        if file.filename == '':
            return 'No se ha seleccionado ningun archivo de video'
        print(file)
        # Ejemplo de c�mo guardar el archivo en el servidor
        ruta = ["src", "static", file.filename]
        ruta_completa = os.path.sep.join(ruta)
        file.save(ruta_completa)
        # Crear una instancia de VideoAnalyzer y pasar el archivo de video y area ROI
        coordinates_str = request.form.get('coordinates', '')
        nameVideo = request.form.get('name', '')
        coordinates_list = parse_roi_area(coordinates_str)
        roiArea = np.array([(punto["x"], punto["y"]) for punto in coordinates_list])  
        area_str = ','.join([f"{coord[0]},{coord[1]}" for coord in roiArea])
        roi_instance = Roi(area_str)
        roi_instance.changeFormat() 
        analyzer = VideoAnalyzer(ruta_completa, roi_instance,nameVideo)
        #print("area_str",area_str)
        print("roiarea",roi_instance.area)
        # Llamar al m�todo analyze() para analizar el video
        result = analyzer.analyze()
        
        # Puedes hacer lo que quieras con el resultado, como mostrarlo en una plantilla
        return render_template('home.html')
    else:
        return 'Metodo no permitido'

@app.route('/uploadVideoCinta', methods=['GET', 'POST'])
def uploadCinta():
    if request.method == 'GET':
        return render_template('uploadVideoCinta.html')
    elif request.method == 'POST':
        if 'file' not in request.files:
            return 'No se ha enviado ningún archivo de video'
        
        # Obteniendo el archivo de video del formulario
        file = request.files['file']
        if file.filename == '':
            return 'No se ha seleccionado ningún archivo de video'
        
        # Guardar el archivo en el servidor
        ruta = ["src", "static", file.filename]
        ruta_completa = os.path.sep.join(ruta)
        file.save(ruta_completa)
        
        # Crear una instancia de VideoAnalyzer y pasar el archivo de video y área ROI
        #--------------------------------
        coordinates_str = request.form.get('coordinates', '')
        nameVideo = request.form.get('name', '')
        coordinates_list = parse_roi_area(coordinates_str)
        roiArea = np.array([(punto["x"], punto["y"]) for punto in coordinates_list])  
        area_str = ','.join([f"{coord[0]},{coord[1]}" for coord in roiArea])
        roi_instance = Roi(area_str)
        analyzerCinta = VideoAnalyzerCinta(ruta_completa, roi_instance, nameVideo)
        #print("roiarea",roi_instance.area)        # Llamar al método analyze() para analizar el video
        result = analyzerCinta.analyze()
        return render_template('home.html')
        # Mostrar el resultado en una plantilla
        #return render_template('home.html', result=result)
    else:
        return 'Método no permitido'
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
