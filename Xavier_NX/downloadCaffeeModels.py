import os
import urllib.request

# URL for the RetinaFace model files
model_urls = [
    'https://github.com/biubug6/Pytorch_Retinaface/raw/master/weights/retinaface-R50.caffemodel',
    'https://github.com/biubug6/Pytorch_Retinaface/raw/master/weights/retinaface-R50.prototxt'
]

# Directory to save the model files
model_dir = 'model/'

# Create the directory if it does not exist
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

# Download the model files
for url in model_urls:
    file_name = os.path.join(model_dir, url.split("/")[-1])
    urllib.request.urlretrieve(url, file_name)

print('RetinaFace model files downloaded successfully!')
