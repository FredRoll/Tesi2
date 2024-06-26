from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap

app = Flask(__name__)


app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)

from survey import routes, models
from survey import db
from survey.models import User, Photoshopper, Image, Preference

#prefs = Preference.query.all()
#images = Image.query.all()
#c= len(images)
#print(c)
#d=0
#for png in images:
#    if(d<=c-3):
#        preference = Preference(user_id=2, photoshopper_id=1, image_id=png.id)
#        db.session.add(preference)
#        db.session.commit()
#        d=d+1
#for pref in prefs:       
#    db.session.delete(pref)
#    db.session.commit()
#    print ("Delete")

# RIMUOVE TUTTE LE IMMAGINI NEL DB
""" with app.app_context():
	images = Image.query.all()
	for image in images:
		db.session.delete(image)
		db.session.commit()
		print("delete " + image.name) """

# AGGIUNGE TUTTE LE IMMAGINI INDICATE DAL FILE test_list.txt
""" #import os #DEBUG
with app.app_context():
	#print(os.path.abspath(os.path.dirname(__file__))) #DEBUG
	test_file_path = 'app/static/imgs/test_list.txt'
	with open(test_file_path, 'r') as file:
		test_imgs_names = [line.strip() for line in file]
	for test_img_name in test_imgs_names:
		#print(test_img_name) #DEBUG
		if test_img_name.endswith('.png'):
			image = Image(name=test_img_name)
			#print(image) #DEBUG
			db.session.add(image)
			db.session.commit()
			#break #DEBUG """

# AGGIUNGE TUTTE LE IMMAGINI INDICATE DAL PATH NEL DB
# pngs = os.listdir('static/imgs/')
# for png in pngs:
# 	if png.endswith('.png'):
# 		image= Image(name=png)
# 		db.session.add(image)
# 		db.session.commit()
# 		print(png)

# ELIMINA LE PREFS DELL'UTENTE CON user_id=x
# x=1:
# for pref in prefs:
#     if pref.user_id==x:
#         db.session.delete(pref)
#         db.session.commit()
#         print ("Delete")