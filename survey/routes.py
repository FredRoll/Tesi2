from flask import render_template, abort, flash, redirect, url_for, request, send_file
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.wrappers import Request
from . import app, db
from .forms import LoginForm, RegistrationForm
from .models import User, Photoshopper, Image, Preference, Test, Question, Answer,TestPreference
from random import shuffle
from flask import session
from urllib.parse import urlparse
import random, os
import array as arr
from flask import Flask, Response
import csv
import json


APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/access_denied')
def access_denied():
   return render_template('access_denied.html')

@app.route('/')
@app.route('/index')
@login_required
def index():
    
    session["storico_preferenze"]=[]                    # Contiene lista immagini id gia testate
    session["c"]=0                           # Contatore +1 ogni volta che vado all'indietro nello storico preferenze
    
    prefs = Preference.query.all()
    images = Image.query.all()
    for pref in prefs:
        if pref.user_id == current_user.id:
            session["storico_preferenze"].append(pref.image_id)
    if (len(images)==len(session["storico_preferenze"])):
        end=True
    else:
        end=False
    
    tests = Test.query.all()
    is_empty = len(tests) == 0

    return render_template('index.html', title='Home',end=end, tests=tests, is_empty=is_empty)


## FUNZIONE PER IL LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Username o Password errate')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)




# FUNZIONE PER CSV DELLE PREFERENZE
@app.route("/prefCSV")
@login_required
def getprefCSV():
 
    photoshoppers = Photoshopper.query.filter(Photoshopper.name != "raw").all()
    pref_counts = {p.name: 0 for p in photoshoppers}

    for pref in Preference.query.filter(Preference.photoshopper_id.in_([p.id for p in photoshoppers])):
        photoshopper = Photoshopper.query.get(pref.photoshopper_id)
        if photoshopper:
            pref_counts[photoshopper.name] += 1

    photoshopper_names = [p.name for p in photoshoppers]
    preference_counts = list(pref_counts.values())

    try:
        with open('app/CSV/data.csv', 'w', newline='') as csvFile:
            writer = csv.writer(csvFile) # , delimiter='\t', quoting=csv.QUOTE_ALL
            writer.writerow(["Photoshopper", "N. Preferenze"])
            writer.writerows(zip(photoshopper_names, preference_counts))
    except Exception as e:
        return f"Error generating CSV: {e}"

    return send_file('CSV/data.csv',
                    mimetype='text/csv',
                    download_name='data.csv',
                    as_attachment=True)




# FUNZIONE PER CSV DEL DATABASE
@app.route("/databaseCSV")
@login_required
def getdbCSV():
    
    prefs = Preference.query.all()
    users = User.query.all()
    name_user = []
    name_image = []
    name_photoshopper= []
    find_name_image=[]
    find_name_photoshopper=[]
    intestazione = ['Nome Utente','Nome Immagine','Nome Photoshopper']
         
    for user in users:
        for pref in prefs:
            if (pref.user_id==user.id):
                name_user.append(user.username)
                find_name_image=Image.query.filter_by(id=pref.image_id).first_or_404()
                name_image.append(find_name_image.name)
                find_name_photoshopper=Photoshopper.query.filter_by(id=pref.photoshopper_id).first_or_404()
                name_photoshopper.append(find_name_photoshopper.name)

    csvData = [(name_user), (name_image), (name_photoshopper)]
    csvData = zip(*csvData)
  
    with open('app/CSV/dataDB.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows([intestazione])
        writer.writerows(csvData)
    csvFile.close()
   
    return send_file('CSV/dataDB.csv',
                         mimetype='text/csv',
                         download_name='dataDB.csv',
                         as_attachment=True)




# FUNZIONE PER IL LOGOUT
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))




# FUNZIONE PER LA REGISTRAZIONE DI UN NUOVO UTENTE
@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulazioni, sei un utente registrato adesso!')
        return redirect(url_for('login'))
        
    return render_template('register.html', title='Register', form=form)
    



# FUNZIONE PER LA REGISTRAZIONE DI UNA NUOVA IMMAGINE
@app.route("/insert_img", methods=['POST','GET'])
@login_required
def insert_img():

    if not current_user.is_admin_user():  # Controllo se l'utente corrente è "admin"
        flash('Accesso negato! Solo l\'utente "admin" può accedere a questa pagina.')
        return redirect(url_for('access_denied'))
    
    error = None
    ext=".png"
    form = RegistrationForm()
    
    if request.method == 'POST':
        text = request.form['text']
        text= text+ext

        exists = db.session.query(Image.id).filter_by(name=text).scalar() is not None
        
        if text == ".png":
            flash('Nome non valido')
            
        elif exists== True:
            flash('Immagine gia esistente!')
            
        else:
            image = Image(name=text)
            db.session.add(image)
            db.session.commit()
            flash('Congratulazioni, immagine aggiunta al database')
        
    return render_template('insert_img.html', form=form)





# FUNZIONE PER LA REGISTRAZIONE DI UN NUOVO TEST
@app.route("/insert_test", methods=['POST','GET'])
@login_required
def insert_test():

    if not current_user.is_admin_user():  # Controllo se l'utente corrente è "admin"
        flash('Accesso negato! Solo l\'utente "admin" può accedere a questa pagina.')
        return redirect(url_for('access_denied'))
    
    error = None
    form = RegistrationForm()
    
    if request.method == 'POST':        
        
        if 'file' not in request.files:
            flash('Nome non valido')

        else:
            file = request.files['file']

            if file.filename == '':
                flash('Nessun file selezionato')
            
            elif file and file.filename.endswith('.json'):

                file_path = 'uploads/' + file.filename

                file.save('uploads/' + file.filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    name = data["name"]
                except KeyError:
                    flash('Formato JSON non valido. Manca la chiave "name" del test.')
                    os.remove(file_path)
                    return render_template('insert_test.html', form=form)

                if db.session.query(Test.id).filter_by(name=name).scalar() is not None:
                    flash('Test gia esistente!')
            
                else:
                    test_db = Test(name=name)
                    db.session.add(test_db)
                    questions_db = []
                    answers_db = []

                    try:
                        questions = data["questions"]
                    except KeyError:
                        flash('Formato JSON non valido. Manca la chiave "questions" del test.')
                        os.remove(file_path)
                        return render_template('insert_test.html', form=form)

                    for question in questions:

                        try:
                            question_value = question["value"]
                            if db.session.query(Question.id).filter_by(value=question_value).filter_by(test_id=test_db.id).scalar() is not None:
                                flash('Una delle question è ripetuta più volte per lo stesso test!')
                                os.remove(file_path)
                                return render_template('insert_test.html', form=form)
                            question_db = Question(value=question_value, test_id=test_db.id)
                            db.session.add(question_db)
                            questions_db.append(question_db)
                        except KeyError:
                            flash('Formato JSON non valido. Manca la chiave "value" di una question.')
                            os.remove(file_path)
                            return render_template('insert_test.html', form=form)

                        try:
                            answers = question["answers"]
                        except KeyError:
                            flash('Formato JSON non valido. Manca la chiave "answers".')
                            os.remove(file_path)
                            return render_template('insert_test.html', form=form)
                        
                        for answer in answers:
                            try:
                                answer_value = answer["value"]
                                is_image = answer.get("is_image", False)
                                if db.session.query(Answer.id).filter_by(value=answer_value).filter_by(question_id=question_db.id).scalar() is not None:
                                    flash('Una delle answer riferite alla stessa question è ripetuta più volte!')
                                    os.remove(file_path)
                                    return render_template('insert_test.html', form=form)
                                answer_db = Answer(value=answer_value,is_image=is_image, question_id=question_db.id)
                                db.session.add(answer_db)
                                answers_db.append(answer_db)
                            except KeyError:
                                flash('Formato JSON non valido. Manca la chiave "value" di una answer.')
                                os.remove(file_path)
                                return render_template('insert_test.html', form=form)

                    db.session.commit()
                    flash('Congratulazioni, test aggiunto al database!')
                
                os.remove(file_path)

            else:
                flash('Tipo di file non valido. Perfavore carica un file JSON.')

    return render_template('insert_test.html', form=form)




# VISUALIZZAZIONE DATI DB
@app.route('/secret')
@login_required
def secret():
    if not current_user.is_admin_user():  # Controllo se l'utente corrente è "admin"
        flash('Accesso negato! Solo l\'utente "admin" può accedere a questa pagina.')
        return redirect(url_for('access_denied'))

    users = User.query.all()
    photoshoppers = Photoshopper.query.all()
    images = Image.query.all()
    prefs = Preference.query.all()
    tests = Test.query.all()
    
    return render_template('users.html', users=users, photoshoppers=photoshoppers, images=images, prefs=prefs, tests=tests)


    
@app.route('/survey_response')
@login_required
def survey_response():
    if not current_user.is_admin_user():  # Controllo se l'utente corrente è "admin"
        flash('Accesso negato! Solo l\'utente "admin" può accedere a questa pagina.')
        return redirect(url_for('access_denied'))

    users = User.query.all()
    tests = Test.query.all()
    
    # Query to get responses
    responses = db.session.query(
    Test.id.label('test_id'),  
    Test.name.label('test_name'), 
    User.username.label('username'), 
    Question.value.label('question'), 
    Answer.value.label('answer')
).select_from(TestPreference)\
 .join(Answer, TestPreference.answer_id == Answer.id)\
 .join(Question, Answer.question_id == Question.id)\
 .join(Test, Question.test_id == Test.id)\
 .join(User)\
 .filter(TestPreference.user_id == User.id)\
 .order_by(Test.id, User.id)\
 .all()

    return render_template('survey_response.html', users=users, tests=tests, responses=responses)


# VISUALIZZAZIONE  GRAFICO (TUTTI GLI UTENTI) E TABELLA (SOLO UTENTE LOGGATO)
@app.route('/grafici')
@login_required
def grafici():

    if not current_user.is_admin_user():  # Controllo se l'utente corrente è "admin"
        flash('Accesso negato! Solo l\'utente "admin" può accedere a questa pagina.')
        return redirect(url_for('index'))
    
    prefs = Preference.query.all()
    photoshopped_images_dir_list = list()
    id_photoshoppers = []
    
    for root, dirs, files in os.walk("./app/static/imgs", topdown=False):
        for name in dirs:
            photoshopped_images_dir_list.append(name)
    
    num_photoshoppers=len(photoshopped_images_dir_list)
    contatore_photoshopper = [0 for photoshopper in range(num_photoshoppers)]
    
    for photoshopper in photoshopped_images_dir_list:
        id_photoshoppers.append(Photoshopper.query.filter_by(name=str(photoshopper)).first_or_404())
         
    for pref in prefs:
        i=0
        for photoshopper in id_photoshoppers:
            if (pref.photoshopper_id==photoshopper.id):
                contatore_photoshopper[i]= contatore_photoshopper[i] +1
            i=i+1

    labels = photoshopped_images_dir_list
    values = contatore_photoshopper
    labels2 = photoshopped_images_dir_list
    values2 = contatore_photoshopper
    colors2 = ["#ffcccc", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#ffffb3", "#ff4d4d", "#c6ffb3"]
    
    return render_template('grafici.html', prefs=prefs, values=values, labels=labels, set=zip(values2, labels2, colors2))

    
 
@app.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    if not current_user.is_admin_user():  # Controllo se l'utente corrente è "admin"
        flash('Accesso negato! Solo l\'utente "admin" può accedere a questa pagina.')
        return redirect(url_for('index'))
    
    photoshoppers = Photoshopper.query.all()
    images = Image.query.all()
    users = User.query.all()
    prefs = Preference.query.all()

    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    for pref in prefs:
        if pref.user_id==user.id:
            db.session.delete(pref)
            db.session.commit()
            print ("Delete")
    db.session.delete(user)
    db.session.commit()

    return render_template('users.html', title='Utenti',users=users, photoshoppers=photoshoppers, images=images)

@app.route('/delete_image', methods=['POST'])
@login_required
def delete_image():
    if not current_user.is_admin_user():  # Controllo se l'utente corrente è "admin"
        flash('Accesso negato! Solo l\'utente "admin" può accedere a questa pagina.')
        return redirect(url_for('index'))
    
    photoshoppers = Photoshopper.query.all()
    images = Image.query.all()
    users = User.query.all()
    prefs = Preference.query.all()

    image_id = request.form.get('image_id')
    image = Image.query.get(image_id)
    db.session.delete(image)
    db.session.commit()

    return render_template('users.html', title='Utenti',users=users, photoshoppers=photoshoppers, images=images)

# # FUNZIONE PER ELIMINARE UN UTENTE
# @app.route('/secret', methods=['POST'])
# @login_required
# def my_form_post():
    
#     photoshoppers = Photoshopper.query.all()
#     images = Image.query.all()
#     users = User.query.all()
#     prefs = Preference.query.all()
    
#     button_clicked = request.form.get('submit')

#     if button_clicked == "Elimina User":
#         u = request.form['text']
#         user = User.query.get(u)
#         for pref in prefs:
#             if pref.user_id==user.id:
#                 db.session.delete(pref)
#                 db.session.commit()
#                 print ("Delete")
#         db.session.delete(user)
#         db.session.commit()
    
#     if button_clicked == "Elimina immagine":
#         u = request.form['text']
#         image = Image.query.get(u)
#         print(image)
#         db.session.delete(image)
#         db.session.commit()
 
#     return render_template('users.html', title='Utenti',users=users, photoshoppers=photoshoppers, images=images) 
  
  
  
# VISUALIZZAZIONE PAGINA TEST FOTO
@app.route('/test')
@login_required
def test():
    
    pathb = r"./app/static/imgs/"
    prefs = Preference.query.all()
    images = Image.query.all()
    photoshopped_images_dir_list = list()
    n= len(session["storico_preferenze"])
    r=len(session["storico_preferenze"])
    n=n-session["c"]

    if session["c"]==0:
        
        print ("c=0")
        
        for root, dirs, files in os.walk("./app/static/imgs", topdown=False):
            for name in dirs:
                if name != "raw":
                    photoshopped_images_dir_list.append(name)
    
        shuffle(photoshopped_images_dir_list)
    
        user_pref=[]
        
        for pref in prefs:
            if pref.user_id==current_user.id:
                user_pref.append(pref.image_id)
        
        id_images=[]
    
        for img in images:
            id_images.append(img.id)
            
        res = list(set(id_images)^set(user_pref))
    
        if not res:
            print("Lista vuota")
            return redirect(url_for('index'))
    
        random_id = random.choice(res)
        rnd = Image.query.filter_by(id=random_id).first_or_404()
        test_img_name= rnd.name

        return render_template("test.html", test_img_name=test_img_name, photoshopped_images_dir_list=photoshopped_images_dir_list, path=pathb, photoshopper_sel="null", n=n, r=r)

    if session["c"]>0:
        
        print ("c>0")
        
        for root, dirs, files in os.walk("./app/static/imgs", topdown=False):
            for name in dirs:
                photoshopped_images_dir_list.append(name)
    
        path = path + photoshopped_images_dir_list[1]
        

        old_img=session["storico_preferenze"][n]
        
        rnd = Image.query.filter_by(id=old_img).first_or_404()
        test_img_name= rnd.name
        photoshopper_sel_id= Preference.query.filter_by(image_id=old_img, user_id=current_user.id).first_or_404()
        photoshopper_sel_name= Photoshopper.query.filter_by(id=photoshopper_sel_id.photoshopper_id).first_or_404()
        
        
        return render_template("test.html", test_img_name=test_img_name, photoshopped_images_dir_list=photoshopped_images_dir_list, path=pathb, photoshopper_sel=photoshopper_sel_name.name,n=n,r=r)

        






## FUNZIONE PER EFFETTUARE UNA PREFERENZA
@app.route("/test", methods = ["GET", "POST"] )
@login_required
def process_form():
    if request.form['b'] == 'Avanti':
        print ("Avanti")
        if session["c"]==0:
            return redirect(url_for('test'))
            
        else:
            session["c"]=session["c"]-1
            return redirect(url_for('test'))
        
    if request.form['b'] == 'Indietro':
        n= len(session["storico_preferenze"])
        if session["c"] < n:
            session["c"]=session["c"]+1
            print ("Indietro")
            return redirect(url_for('test'))
        else:
            return redirect(url_for('test'))
        
    else:
        
        photoshopper_form = request.form.getlist('b')
        user_match = User.query.filter_by(username=current_user.username).first()
        photoshopper_match = Photoshopper.query.filter_by(name=''.join(photoshopper_form)).first_or_404()
        
        if session["c"]>0:
            n= len(session["storico_preferenze"])
            n=n-session["c"]
            

            modifica= Preference.query.filter_by(image_id=session["storico_preferenze"][n], user_id=user_match.id).first()
            modifica.photoshopper_id=photoshopper_match.id
            session["photoshopper"]=photoshopper_match.name
            print (modifica.photoshopper_id)
            db.session.commit()
            session["c"]=session["c"]-1
            
            
            
        else:
            
            a = request.form.getlist('text')
            img_form = a[0]     
            
            image_match = Image.query.filter_by(name=img_form).first_or_404()
            preference = Preference(user_id=user_match.id, photoshopper_id=photoshopper_match.id, image_id=image_match.id)
            db.session.add(preference)
            db.session.commit()
            session["storico_preferenze"].append(image_match.id)
            session["c"]=0

    
        return redirect(url_for('test'))



@app.route("/index", methods = ["POST","GET"] ) 
@login_required
def contact():        
    if request.form['a'] == 'Elimina preferenze':
        prefs = Preference.query.all()
        for pref in prefs:   
            db.session.delete(pref)
            db.session.commit()
        return render_template('index.html')



@app.route('/start_test')
def start_test():
    test_id = request.args.get('test')
    test = Test.query.get(test_id)
    if not test:
        abort(404)
    else:
        questions = Question.query.filter_by(test_id=test.id).all()
        for question in questions:
            question.answers = Answer.query.filter_by(question_id=question.id).all()
        return render_template('start_test.html', test=test, questions=questions)



@app.route('/submit_test', methods=['POST'])
def submit_test():
    user_id = current_user.id
    form_data = request.form
    print("Contenuto del form:", form_data)  

    try:
        
        for key in form_data:
            if key.startswith('question_'):
                question_id = key.split('_')[1]  
                answer_id = form_data[key]  
                answer = Answer.query.get(int(answer_id))
                if answer and answer.question_id == int(question_id):
                    test_preference = TestPreference(user_id=user_id, answer_id=answer.id)
                    db.session.add(test_preference)
                    print(f"Aggiunto TestPreference: {test_preference}")  # Debug dell'oggetto creato
                else:
                    print(f"Nessuna risposta valida trovata per question_id: {question_id} con answer_id: {answer_id}")
        
        db.session.commit()
    except Exception as e:
        print(f"Si è verificato un errore: {e}")
        db.session.rollback()
        return redirect(url_for('start_test'))

    return redirect(url_for('end_test'))


@app.route('/end_test')
def end_test():
    return render_template('end_test.html')




    

# Nome utente header
# Contatore immagini rimanenti
# Togliere button "indietro" quando sono a coda lista
# Consentire ad admin tutte funzionalita

#screen
# flask run -- host= 0.0.0.0

# ctrl +a  -----> d
# screen - r recupero
