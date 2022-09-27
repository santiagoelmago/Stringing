from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy.sql import text, func
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt


app = Flask(__name__)

db_name = 'racketinfo.db'
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['SECRET_KEY'] = 'thisisasecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

class RacketForm(db.Model):
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
    created_on = db.Column(DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
 
    def __repr__(self):
        return '<RacketForm %r>' % self.player_name

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

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

    #Lines 38–53 provide a model so that Python can translate the racket info table.

@app.route("/racket", methods= ["GET", "POST"])
@login_required
def rackets():
    if request.method == "POST":
        racket_form_response = RacketForm(
            player_name = request.form.get('player_name'), 
            phone_number = request.form.get('phone_number'), 
            racket_brand = request.form.get('racket_brand'),
            racket_model = request.form.get('racket_model'),
            string_main = request.form.get('string_main'),
            string_cross = request.form.get('string_cross'),
            tension = request.form.get('tension'),
            status = "In Progress",
            payment = request.form.get('paid') == 'on',
            created_on = request.form.get('created_on'),
            updated_on = request.form.get('updated_on')
            ) 

        db.session.add(racket_form_response)
        db.session.commit()
        return redirect(url_for('rackets'))
    if request.method == "GET":
        rackets = RacketForm.query.order_by(RacketForm.status.desc(), RacketForm.created_on.desc()).all()
        return render_template("racket_queue.html", rackets=rackets)



@app.route("/racket/new", methods= ["GET"])
@login_required
def createRacket():
    return render_template('form.html')

@app.route("/racket/<int:racket_id>", methods= ["POST"])
@login_required
def update(racket_id):
    if request.method == "POST":
        racket_request = RacketForm.query.filter_by(id=racket_id).first()
        racket_request.status = request.form.get('status')
        racket_request.stringer = request.form.get('stringer')
        racket_request.payment = request.form.get('paid') == 'on'
        db.session.commit()
        return redirect(url_for('rackets'))

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
        hashed_password = bcrypt.generate_password_hash(form.password.data)
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

# NOTHING BELOW THIS LINE NEEDS TO CHANGE
# this route will test the database connection and nothing more

@app.route('/testdb')
def testdb():
    try:
        db.session.query(text('1')).from_statement(text('SELECT 1')).all()
        return '<h1>It works.</h1>'
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)