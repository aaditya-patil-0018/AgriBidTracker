# importing needed modules
import numpy as np
import tensorflow
import cv2
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def detect(image):
    ## Loading Model
    cnn = tensorflow.keras.models.load_model("fruit_disease_detection_model.h5")

    ## Testing Model
    image = tensorflow.keras.preprocessing.image.load_img(image, target_size=(64,64))
    input_array = tensorflow.keras.preprocessing.image.img_to_array(image)
    input_array = np.array([input_array]) # converting single image to batch
    prediction = cnn.predict(input_array)

    # changes needed in the path
    test_dataset = tensorflow.keras.utils.image_dataset_from_directory(
        "../fruit_disease_dataset/data/test/",
        labels = "inferred",
        label_mode = "categorical",
        class_names = None,
        color_mode = "rgb",
        batch_size = 32,
        image_size = (64,64),
        shuffle = True,
        seed = None,
        validation_split = None,
        subset = None,
        interpolation = "bilinear",
        follow_links = False,
        crop_to_aspect_ratio = False
    )
    
    td = os.listdir("../fruit_disease_dataset/data/test/")

    # test_dataset.class_names
    result_index = np.where(prediction[0] == max(prediction[0]))

    # Single Prediction
    print(f"Fruit is: {test_dataset.class_names[result_index[0][0]]}")
    print(f"Fruit is: {td[result_index[0][0]]}")
    return test_dataset.class_names[result_index[0][0]]

if __name__ == "__main__":
    image = input("Enter image path: ")
    detect(image)
