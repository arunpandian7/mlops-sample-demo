from keras.api.models import load_model
import cv2
import numpy as np
import warnings
warnings.filterwarnings("ignore")

model = load_model("effnet-latest.keras")

class_result_map = {
    0: "Glioma Tumor",
    1: "Beningn Tumor/No Tumor",
    2: "Meningioma Tumor",
    3: "Pituitory Tumor",
}


def predict_from_image_path(image_path: str) -> str:
    print(image_path)
    image = cv2.imread(image_path)
    img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    img = cv2.resize(img, (150, 150))
    img = np.expand_dims(img, axis=0)
    prediction = model.predict(img)
    print(prediction)
    prediction = np.argmax(prediction, axis=1)[0]
    print(prediction)
    prediction_class = class_result_map[prediction]
    return prediction_class

if __name__ == "__main__":
    r = predict_from_image_path("./images/image(15).jpg")
    print(r)