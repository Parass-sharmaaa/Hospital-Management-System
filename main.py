from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, login_required, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required,current_user
from flask_mail import Mail
import json

with open(r'C:\Users\pc\Desktop\DBMS CHECK\FLASK-DBMS-PROJECT\config.json', 'r') as c:

    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'DBMS'

# Configuring the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/hms'
db = SQLAlchemy(app)

# Setting up Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# SMTP MAIL SERVER SETTINGS

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='587',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Defining models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(1000))

class Doctors(db.Model):
    did = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    doctorname = db.Column(db.String(50))
    dept = db.Column(db.String(50))

class Patients(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    name = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    slot = db.Column(db.String(50))
    disease = db.Column(db.String(50))
    time = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    dept = db.Column(db.String(50))
    number = db.Column(db.String(50))

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/doctors', methods=['POST', 'GET'])
def doctors():
    if request.method == "POST":
        email = request.form.get('email')
        doctorname = request.form.get('doctorname')
        dept = request.form.get('dept')

        new_doctor = Doctors(email=email, doctorname=doctorname, dept=dept)
        db.session.add(new_doctor)
        db.session.commit()
        flash("Information is Stored", "primary")

    return render_template('doctor.html')

@app.route('/patients', methods=['POST', 'GET'])
@login_required
def patient():
    doct = Doctors.query.all()

    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        gender = request.form.get('gender')
        slot = request.form.get('slot')
        disease = request.form.get('disease')
        time = request.form.get('time')
        date = request.form.get('date')
        dept = request.form.get('dept')
        number = request.form.get('number')
        subject = "HOSPITAL MANAGEMENT SYSTEM"

        new_patient = Patients(email=email, name=name, gender=gender, slot=slot, disease=disease,
                               time=time, date=date, dept=dept, number=number)
        db.session.add(new_patient)
        db.session.commit()

        # Uncomment this section if you want to send an email
        mail.send_message(subject, sender=params['gmail-user'], recipients=[email], body=f"YOUR bOOKING IS CONFIRMED THANKS FOR CHOOSING US \nYour Entered Details are :\nName: {name}\nSlot: {slot}")

        flash("Booking Confirmed", "info")

    return render_template('patient.html', doct=doct)

@app.route('/bookings')
@login_required
def bookings():
    em = current_user.email
    query = Patients.query.filter_by(email=em).all()
    return render_template('booking.html', query=query)

@app.route("/edit/<int:pid>", methods=['POST', 'GET'])
@login_required
def edit(pid):
    patient = Patients.query.get_or_404(pid)
    if request.method == "POST":
        patient.email = request.form.get('email')
        patient.name = request.form.get('name')
        patient.gender = request.form.get('gender')
        patient.slot = request.form.get('slot')
        patient.disease = request.form.get('disease')
        patient.time = request.form.get('time')
        patient.date = request.form.get('date')
        patient.dept = request.form.get('dept')
        patient.number = request.form.get('number')
        db.session.commit()
        flash("Slot is Updated", "success")
        return redirect('/bookings')
    
    return render_template('edit.html', patient=patient)

@app.route("/delete/<int:pid>", methods=['POST', 'GET'])
@login_required
def delete(pid):
    patient = Patients.query.get_or_404(pid)
    db.session.delete(patient)
    db.session.commit()
    flash("Slot Deleted Successfully", "danger")
    return redirect('/bookings')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist", "warning")
            return render_template('signup.html')
        encpassword = generate_password_hash(password)

        new_user = User(username=username, email=email, password=encpassword)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup Successful, Please Login", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Success", "primary")
            return redirect(url_for('index'))
        else:
            flash("Invalid Credentials", "danger")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))

# Add more routes as needed...

if __name__ == '__main__':
    app.run(debug=True)
