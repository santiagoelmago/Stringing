"""Stringing app server.

Main module that hold CRUD logic for app operations.
"""

import os
from datetime import date, datetime

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy.sql import text, func
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt


app = Flask(__name__)

bcrypt = Bcrypt(app)

# Database configuration.
_DB_USER = os.getenv('POSTGRES_USER')
_DB_PD = os.getenv('POSTGRES_PASSWORD')
_DB_NAME = os.getenv('POSTGRES_DB')
_DB_CONTAINER = os.getenv('DATABASE_CONTAINER')
# Database URL is the ENV var passed from heroku postgres.
_DATABASE_URL = os.getenv("DATABASE_URL")
if _DATABASE_URL.startswith("postgres://"):
    _DATABASE_URL = _DATABASE_URL.replace("postgres://", "postgresql://", 1)

if _DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = _DATABASE_URL
else:
    _SEPARATE_URL = f'postgresql://{_DB_USER}:{_DB_PD}@{_DB_CONTAINER}:5432/{_DB_NAME}'
    app.config['SQLALCHEMY_DATABASE_URI'] = _SEPARATE_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# High level entrypoint to database execution.
db = SQLAlchemy(app)

# Authentication configuration.
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Racket(db.Model):
    __tablename__ = 'rackets'
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(80), unique=False, nullable=False)
    stringer = db.Column(db.String(80), unique=False, nullable=True)
    phone_number = db.Column(db.String(80), unique=False, nullable=False)
    racket_brand = db.Column(db.String(120), unique=False, nullable=False)
    racket_model = db.Column(db.String(80), unique=False, nullable=False)
    string_main = db.Column(db.String(80), unique=False, nullable=False)
    string_cross = db.Column(db.String(80), unique=False, nullable=False)
    tension = db.Column(db.Integer, unique=False, nullable=False)
    status = db.Column(db.String(80), unique=False, nullable=False)
    payment = db.Column(db.Boolean, unique=False, nullable=False)
    created_on = db.Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_on = db.Column(DateTime(timezone=True),
                           default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<Racket %r>' % self.player_name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route("/")
@login_required
def home():
    return render_template('home.html')


@app.route("/racket", methods=["GET", "POST"])
@login_required
def rackets():
    if request.method == "POST":
        racket_form_response = Racket(
            player_name=request.form.get('player_name'),
            phone_number=request.form.get('phone_number'),
            racket_brand=request.form.get('racket_brand'),
            racket_model=request.form.get('racket_model'),
            string_main=request.form.get('string_main'),
            string_cross=request.form.get('string_cross'),
            tension=request.form.get('tension'),
            status="In Progress",
            payment=request.form.get('paid') == 'on',
            created_on=request.form.get('created_on'),
            updated_on=request.form.get('updated_on')
        )

        db.session.add(racket_form_response)
        db.session.commit()
        return redirect(url_for('rackets'))

    #if request.method == "GET":
        #Will only work with databases other than sqlite and in timezone MST.
        #finished_today = RacketForm.query.filter(RacketForm.updated_on == date.today(), RacketForm.status == "Finished").count()
        # Will only work with databases other than sqlite and in timezone MST.
        #orders_today = RacketForm.query.filter(RacketForm.created_on == date.today()).count()
        #items = RacketForm.query.order_by(RacketForm.status.desc(), RacketForm.created_on.desc()).all()
        #return render_template("racket_queue.html", rackets=items, orders_today=orders_today, finished_today=finished_today)


@app.route("/racket/new", methods=["GET"])
@login_required
def createRacket():
    return render_template('form.html')


@app.route("/racket/<int:racket_id>", methods=["POST"])
@login_required
def update(racket_id):
    if request.method == "POST":
        racket_request = Racket.query.filter_by(id=racket_id).first()
        racket_request.status = request.form.get('status')
        racket_request.stringer = request.form.get('stringer')
        racket_request.payment = request.form.get('paid') == 'on'
        db.session.commit()
        return redirect(url_for('rackets'))


@app.route('/racket/<int:racket_id>/delete', methods=["GET", "POST"])
@login_required
def delete(racket_id):
    racket = Racket.query.filter_by(id=racket_id).first()

    if request.method == "POST":
        db.session.delete(racket)
        db.session.commit()
        return render_template('delete_success.html', racket=racket)

    if request.method == "GET":
        return render_template('delete_confirmation.html', racket=racket)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('rackets'))
    return render_template('login.html', form=form)


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/history', methods=["GET"])
@login_required
def history():
    return render_template('history.html')


@app.route('/inventory', methods=["GET"])
@login_required
def inventory():
    return render_template('inventory.html')


@app.route('/stringers', methods=["GET"])
@login_required
def stringers():
    return render_template('stringers.html')


@app.route('/customers', methods=["GET"])
@login_required
def customers():
    return render_template('customers.html')


# This route will test the database connection and nothing more
@app.route('/healthcheck')
def healthcheck():
    try:
        db.session.query(text('1')).from_statement(text('SELECT 1')).all()
        return '<h1>It works.</h1>'
    except Exception as error:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(error) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text, 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=os.getenv('DEBUG') == 'True',
            host='0.0.0.0', port=os.getenv('PORT'))
