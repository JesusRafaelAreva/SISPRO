from tensorflow import keras
import cv2
import numpy as np
import os

model = keras.models.load_model("C:\\Users\\ASUS\\Desktop\\proyect\\model\\ThisModel.h5")
resize = 60


def preprocess_image(image):
    image = cv2.imread(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 
    image = cv2.resize(image, (resize, resize)) /255
    image = np.array(image)
    image = np.expand_dims(image, axis=0)
    return image

def prediction(image):

    if not os.path.isfile(image):
       print("Imagen No Identificada: {}".format(image))
       return "Image not found"
       
    image = preprocess_image(image)
    output = model.predict(image)
    output = np.argmax(output, axis=1)
    
    if output == 0:
        return 'Covid-19'
    elif output == 1:
        return 'Opacidad_pulmonar'
    elif output == 2:
        return 'Normal'
    elif output == 3:
        return 'Pneumonia'
    elif output == 4:
        return 'Cáncer_de_pulmón'
    else:
        return 'Imagen no válida'
