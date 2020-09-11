import os, secrets, re

#from datetime import datetime
from PIL import Image # Pillow

from bandz import app, pictures_folder

profile_pics = os.path.join(pictures_folder, "user_profile_pics")
band_pics = os.path.join(pictures_folder, "band_profile_pics")


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
# // output_dir not band
def save_picture(form_picture, band=False, output_size=default_size ):
    rand_hex = secrets.token_hex(8)
    _fn, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = rand_hex + f_ext
    if band:
        picture_path = os.path.join(band_pics, picture_fn)
        output_size = (400, 400)
    else:
        picture_path = os.path.join(profile_pics, picture_fn)
        # url_for('static_media', filename="user_profile_pics/" + current_user.image_file)
    # resize
    i = Image.open(form_picture)
    #i.thumbnail(output_size)
    i = i.resize(output_size)
    i.save(picture_path)

    return picture_fn


#lstrip , rstrip and hashtag cataloging
# regex split
def de_article(bandname):
    articles = {'a': '', 'an':'', 'the':''}
    _band_name = []
    _articles = []
    for word in bandname.split():
        _articles.append(word) if word.lower() in articles else _band_name.append(word)
    if len(_articles) > 0:
        _bandname = ' '.join(_band_name) + ', ' + ' '.join(_articles)
    else:
        _bandname = ' '.join(_band_name)
    return _bandname


def de_singularise(artistname):
    _artist = artistname.split()
    return _artist[-1] + ', ' + (" ").join(_artist[:-1])