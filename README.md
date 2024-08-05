# Herramienta de Muestreo

“Herramienta de Muestreo para Procesos de Simulación de Eventos Discretos Integrando Modelos de Aprendizaje Profundo sobre Redes Neuronales”
** Develop **
------------------------------------------------------------Notas de Emanuel------------------------------------------------------------------------ 
Se tiene que instalar anaconda o un programa similar para utilizar un ambiente de python, esto debido a la librerían dlib
primero se debe crear el ambiente de la siguiente manera:
py -m venv nombreAmbiente
luego se debe instalar flask y todas las librerías necesarias
pip install flask
pip install cv2
cd app
nombreAmbiente\Scripts\activate
python wsgi.py

** Sobre el modelo para la cinta transportadora **
El modelo fue generado con yolov8, se utilizaron las siguientes posibles identificaciones vacio, carrito vacio, carrito incompleto y carrito completo.
1: 'vacio', 3: "carrito completo", 2: "Carrito incompleto", 0: "Carrito vacio"
El etiquetado de las imagenes se realizó en supervisely, es una plataforma web para etiquetado de imagenes bastante buena. Utilizando la cuenta de google de la aplicación se puede entrar en la plataforma y se van a encontrar las imagenes utilizadas para el entrenamiento del modelo etiquetadas, estás etiquetas se pueden quitar o modificar. En el drive se encuentra un archivo .tar, este es un archivo que guarda el proyecto de supervisely.
En la carpeta de creación de modelos se encuentra lo necesario para crear y probar nuevos modelos.

---------------------------------------------------------Fin de las notas de Emanuel---------------------------------------------------------------------------------

** Production **
Gcloud shell deploy
update repo
export PROJECT_ID=formsappdb 
echo $PROJECT_ID  
gcloud builds submit -t gcr.io/$PROJECT_ID/k8s_api/pi-sampling-tool:v0.1.0 .

gcloud container clusters get-credentials cluster-py -z=us-central1
kubectl config current-context
kubectl apply -f timeTracker.yaml