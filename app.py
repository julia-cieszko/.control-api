from flask import Flask, request
from flask_cors import CORS, cross_origin
from firebase_admin import credentials, firestore, initialize_app
import requests
from io import BytesIO
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import tensorflow as tf
from google.cloud.firestore_v1 import ArrayUnion
import datetime
import psutil
import resource

# Calculate the maximum memory limit (80% of available memory)
virtual_memory = psutil.virtual_memory()
available_memory = virtual_memory.available
memory_limit = int(available_memory * 0.8)

# Set the memory limit
resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

cred = credentials.Certificate('admin.json')
initialize_app(cred, {'storageBucket': 'dermatologyapp-bed75.appspot.com'})
db = firestore.client()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

model = load_model('model_full_densenet_isic18_97_88.h5')
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
CLASSES = np.array(['melanoma', 'non-melanoma'])


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/analyze', methods=['POST'])
@cross_origin()
def analyze():
    content_type = request.headers['content-type']
    if content_type == "application/json":
        data = request.json
        caller = data["caller"]
        lid = data["lesionId"]
        print(data['photoUrl'])
        print(data['photoUrl'].replace("photos/", "photos%2F"))
        x = data['photoUrl'].replace("photos/", r"photos%2F")
        print(x)
        y = data['photoUrl'].replace("photos/", "photos%2F")
        print(y)
        z = data["photoUrl"].index("photos/")
        print(z)
        img_res = requests.get(data['photoUrl'].replace("photos/", "photos%2F"))
        img = Image.open(BytesIO(img_res.content))
        img.save('test.jpg')
        img_scaled = img.resize((224, 224))
        arr = np.asarray(img_scaled)
        arr = arr / 255.0
        arr = arr.reshape((1, 224, 224, 3))
        img = image.load_img('test.jpg', target_size=(224, 224))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        x = model.predict(img, verbose=2)
        ps = CLASSES[np.argmax(x, axis=-1)]
        # ps = ["melanoma"]
        print(ps)
        # print(np.argmax(x, axis=-1))
        print(data)
        if caller == "add":
            _, lesion_ref = db.collection('lesions').add({
                'diagnostics': ps[0],
                'quality': np.max(x, axis=-1).tolist(),
                # 'quality': [0.69],
                'photoUrl': [data['photoUrl'].replace("photos/", "photos%2F")],
                'symptoms': data['symptoms'],
                'location': data['location'],
                'bodySide': data['bodySide'],
                'photosTimestamps': [datetime.datetime.now()]
            })
            db.collection('users').document(data['uid']).update({
                'lesions': ArrayUnion([lesion_ref.id])
            })
            db.collection("lesions").document(lesion_ref.id).update({
                "id": lesion_ref.id
            })
            return {'diagnostics': ps[0], 'quality': np.max(x, axis=-1).tolist()}
        elif caller == "update":
            db.collection("lesions").document(lid).update({
                "photoUrl": ArrayUnion([data["photoUrl"].replace("photos/", "photos%2F")]),
                "quality": ArrayUnion(np.max(x, axis=-1).tolist()),
                "photosTimestamps": ArrayUnion([datetime.datetime.now()])
            })
            return {'diagnostics': ps[0], 'quality': [0.69]}
        else:
            return {'result': 'error', 'message': 'Invalid content type'}, 400
    return {'result': 'error', 'message': 'Invalid content type'}, 400


if __name__ == '__main__':
    app.run()
