import os, secrets, re
#from datetime import datetime
from PIL import Image # Pillow

def extract_tags(tags):
    whitespace = re.compile('\s')
    nowhite = whitespace.sub("", tags)
    tags_array = nowhite.split(',')

    cleaned = []
    for tag in tags_array:
        if tag not in cleaned and tag != "":
            cleaned.append(tag)
    
    return cleaned


default_size = (125, 125)
def save_picture(form_picture, output_size=default_size ):
    rand_hex = secrets.token_hex(8)
    _fn, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = rand_hex + f_ext
    picture_path = os.path.join(profile_pics, picture_fn)
    # url_for('static_media', filename="user_profile_pics/" + current_user.image_file)
    # resize
    i = Image.open(form_picture)
    #i.thumbnail(output_size)
    i = i.resize(output_size)
    i.save(picture_path)

    return picture_fn