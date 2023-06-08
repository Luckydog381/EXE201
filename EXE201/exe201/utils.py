import os
import secrets
from PIL import Image
from exe201 import app, db
from exe201.models import User, Profile, Artist, Product, Cart

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


# Create fake data
def create_product_info():
    product1 = Product(name = 'Bugs bunny 1', image_link = 'img/meme_1.jpg', price = 32, description = 'This is product 1', creator = 1)
    product2 = Product(name = 'Bugs bunny 2', image_link = 'img/meme_2.jpg', price = 10, description = 'This is product 2', creator = 2)
    product3 = Product(name = 'Bugs bunny 3', image_link = 'img/meme_3.jpg', price = 50, description = 'This is product 3', creator = 3)
    product4 = Product(name = 'Bugs bunny 4', image_link = 'img/meme_4.jpg', price = 100, description = 'This is product 4', creator = 1)

    db.session.add(product1)
    db.session.add(product2)
    db.session.add(product3)
    db.session.add(product4)
    db.session.commit()