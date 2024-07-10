import os
import json
from flask import render_template, abort, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse

from . import app, db
from .forms import LoginForm, RegistrationForm
from .models import User, Test, Question, Answer, TestPreference

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/access_denied')
def access_denied():
   return render_template('access_denied.html')


@app.route('/')
@app.route('/index')
@login_required
def index():
    tests = Test.query.all()
    is_empty = len(tests) == 0
    return render_template('index.html', title='Home', tests=tests, is_empty=is_empty)


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
    

# FUNZIONE PER LA REGISTRAZIONE DI UN NUOVO TEST
@app.route("/insert_test", methods=['POST','GET'])
@login_required
def insert_test():
    if not current_user.is_admin_user():  # Controllo se l'utente corrente è "admin"
        flash('Accesso negato! Solo l\'utente "admin" può accedere a questa pagina.')
        return redirect(url_for('access_denied'))
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
@app.route('/survey_response')
@login_required
def survey_response():
    if not current_user.is_admin_user():  
        flash('Accesso negato! Solo l\'utente "admin" può accedere a questa pagina.')
        return redirect(url_for('access_denied'))

    users = User.query.all()
    tests = Test.query.all()
    
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
