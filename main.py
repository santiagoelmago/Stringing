from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy.sql import text, func

app = Flask(__name__)

db_name = 'racketinfo.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

class RacketForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(80), unique=False, nullable=False)
    phone_number = db.Column(db.String(80), unique=False, nullable=False)
    racket_brand = db.Column(db.String(120), unique=False, nullable=False)
    racket_model = db.Column(db.String(80), unique=False, nullable=False)
    string_main = db.Column(db.String(80), unique=False, nullable=False)
    string_cross = db.Column(db.String(80), unique=False, nullable=False)
    tension = db.Column(db.Integer, unique=False, nullable=False)
    status = db.Column(db.String(80), unique=False, nullable=False)
    created_on = db.Column(DateTime(timezone=True), server_default=func.now())
    updated_on = db.Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
 
    def __repr__(self):
        return '<RacketForm %r>' % self.player_name

@app.route("/")
def home():
    return render_template('home.html')

    #Lines 38–53 provide a model so that Python can translate the racket info table.

@app.route("/form", methods= ["POST"])
def form():
    racket_form_response = RacketForm(
        player_name = request.form.get('player_name'), 
        phone_number = request.form.get('phone_number'), 
        racket_brand = request.form.get('racket_brand'),
        racket_model = request.form.get('racket_model'),
        string_main = request.form.get('string_main'),
        string_cross = request.form.get('string_cross'),
        tension = request.form.get('tension'),
        status = "In Progress",
        created_on = request.form.get('created_on'),
        updated_on = request.form.get('updated_on')
        ) 

    db.session.add(racket_form_response)
    db.session.commit()
    return redirect(url_for('racketqueue'))

@app.route("/racketqueue")
def racketqueue():
    rackets = RacketForm.query.order_by(RacketForm.status.desc(), RacketForm.created_on.desc()).all()

    return render_template("racket_queue.html", rackets=rackets)

@app.route("/update/<int:racket_id>/status/<string:status>")
def update(racket_id, status):
    racket_request = RacketForm.query.filter_by(id=racket_id).first()
    racket_request.status = status
    db.session.commit()
    return redirect(url_for('racketqueue'))


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