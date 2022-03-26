import os

import PyPDF2
from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, validators
from wtforms.validators import InputRequired, Length, ValidationError

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

migrate = Migrate(app, db)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    password_confirm = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    student_id = db.Column(db.Integer, nullable=False, unique=True)
    mobile_number = db.Column(db.Integer, nullable=False, unique=True)


class PrintQueue(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customer = db.relationship(lambda: User, uselist=False)
    file_location = db.Column(db.String(520), nullable=False, unique=True)
    total_copies = db.Column(db.Integer, nullable=False, unique=False)
    pages = db.Column(db.String(120), nullable=False, unique=False)
    total_cost = db.Column(db.Float, nullable=False, unique=False)
    print_progress_status = db.Column(db.String(120), nullable=False, unique=False)
    payment_method = db.Column(db.String(120), nullable=False, unique=False)
    payment_transaction_id = db.Column(db.String(120), nullable=False, unique=True)
    payment_verification_status = db.Column(db.String(120), nullable=False, unique=False)

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(PrintQueue, db.session))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasceretkey'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegisterForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(
        min=4, max=200)], render_kw={"placeholder": "Enter Your Full Name"})

    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20), validators.EqualTo('password_confirm', message='Passwords must match')], render_kw={"placeholder": "Password"})

    password_confirm = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Confirm Your Password"})

    email = StringField(validators=[InputRequired(), Length(
        min=10, max=120)], render_kw={"placeholder": "Email Address"})

    student_id = StringField(validators=[InputRequired(), Length(
        min=4, max=8)], render_kw={"placeholder": "Enter Your ID Number"})

    mobile_number = StringField(validators=[InputRequired(), Length(
        min=4, max=12)], render_kw={"placeholder": "Enter Your Mobile Number"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()

        if existing_user_username:
            raise ValidationError(
                "That username already exist. Please choose a different one")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")


@ app.route('/')
def home():
    return render_template('home.html')


@ app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                # return render_template('dashboard.html', username=user.username)
                return redirect(url_for('uploadfile', username=user.username))
    return render_template('login.html', form=form)


@ app.route("/dashboard", methods=['GET', 'POST'])
@ login_required
def dashboard():
    return render_template('dashboard.html')


@ app.route("/uploadfile", methods=['GET', 'POST'])
def uploadfile():
    if request.method == 'POST':
        # Handle POST Request here

        if request.files:
            f = request.files['file']
            # name = str(request.form['person'])
            name = request.args['username']
            filename = secure_filename(f.filename)
            path = 'static/upload/file/' + name
           # x = os.mkdir(path)

           # IF Else loop for checking the directory exists or not
            if os.path.isdir(path) == True:
                print(path)
            else:
                os.mkdir(path)

            # If Else Loop Ends

            print(path)
            filePath = os.path.join(path, filename)

            # IF Else loop for checking the same name file exists in the directory
            if os.path.isfile(filePath) == True:
                os.remove(filePath)
                print('work on IF')
                f.save(filePath)
            else:
                f.save(filePath)
                print('Work on Else')
            print(filePath)
            # IF Else loop for checking the same name file exists in the directory

            # Code for PDF Page Counter
            sample_pdf = open(filePath, mode='rb')
            pdfdoc = PyPDF2.PdfFileReader(sample_pdf)
            # print(pdfdoc.numPages)
            pageNumber = pdfdoc.numPages
            # Code for PDF Page Counter

            # Showing PDF and Print option to user
            # pdf_file = url_for('uploadfile', filename=filename)

            # print(pdf_file)
            # acrobat = 'C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe'
            # name = win32print.GetDefaultPrinter()
            # cmd = '"{}" /n /o /t "{}" "{}"'.format(acrobat, pdf_file, name)
            # for i in range(1):
            #     proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
            #                             stderr=subprocess.PIPE)
            # Showing PDF and Print option to user

            # Cost Calculation section
            totalCost = pageNumber * 3
            print(totalCost)
            # Cost Calculation section

            return render_template('upload_print.html', pageNumber=pageNumber, filename=filename, filePath=filePath, username=name, totalCost=totalCost)
    return render_template('dashboard.html')


@app.route("/test_ui", methods=['GET'])
def testing_ui():
    pdf_file_path = '/static/upload/file/hedayet/azurefundamentals.pdf'

    with open(pdf_file_path[1:], mode='rb') as pdf:
        pdfdoc = PyPDF2.PdfFileReader(pdf)
        pg = pdfdoc.numPages

    return render_template('print_options.html',
                           pageNumber=pg,
                           filename='bkash',
                           filePath=pdf_file_path,
                           unit_price=3,
                           username='mrahman'
                           )


@app.route("/doc_to_print", methods=['GET'])
def get_data_to_print():
    data = PrintQueue.query.filter(PrintQueue.print_progress_status == 'in queue').order_by(PrintQueue.id).all()
    data = [dict(id=row.id, pages=row.pages, src=row.file_location, copies=row.total_copies) for row in data]
    return jsonify(data)


@app.route("/accept_print_info", methods=['POST'])
def print_details():
    data = request.form.to_dict()
    return jsonify(data)


@app.route("/print_success", methods=['POST'])
def print_details():
    data = request.form.to_dict()
    if data.get('task_id'):
        row_id = data['task_id']

    return jsonify(data)


@ app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name=form.name.data, username=form.username.data,
                        password=hashed_password, password_confirm=hashed_password, email=form.email.data, student_id=form.student_id.data, mobile_number=form.mobile_number.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('registration.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
