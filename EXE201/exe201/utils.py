import os
import secrets
from PIL import Image
from exe201 import app, db

def save_image(image_file, folder):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(image_file.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, folder, picture_fn)
    output_size = (500, 500)
    i = Image.open(image_file)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn