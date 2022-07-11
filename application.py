from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import *
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
import pickle
import math
import numpy as np
from datetime import date

application = Flask(__name__)
db = SQLAlchemy(application)
bcrypt = Bcrypt(application)


application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tongharry:Tw042565?@mydb.cagovpenmcir.us-west-1.rds.amazonaws.com/userdatabase'
application.config['SECRET_KEY'] = 'harrytong'

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = "index"

with open ('saved_model.pkl', 'rb') as file:
    data = pickle.load(file)


le_location = data["le_location"]

linear_predict = data["linear"]
decision_predict = data["decision"]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):

    __tablename__  = 'user'

    id = db.Column(db.INT, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

class Posts(db.Model):

    __tablename__ = 'posts'

    PostID = db.Column(db.INT, nullable = False, primary_key = True)
    id = db.Column(db.INT, db.ForeignKey('user.id'), nullable = False)
    company = db.Column(db.String(40), nullable = False)
    base_salary = db.Column(db.INT, nullable = False)
    bonus_salary = db.Column(db.INT, nullable = False)
    date_posted = db.Column(db.Date, nullable = False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def check_user(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError("User already exists")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)])

    submit = SubmitField("Login")


@application.route('/', methods=['POST', 'GET'])
def index():

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if (user):
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Hello World")
                return redirect(url_for('forum'))

    return render_template('index.html', form=form)


@application.route('/register', methods=['POST', 'GET'])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        hashed = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name=form.username.data, password=hashed)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@application.route('/predict', methods=['POST', 'GET'])
@login_required
def predict():

    if request.method == 'POST':
        location = request.form['location']
        
        if (location == "Default"):
            return render_template('predict.html')
        years = request.form['yearsofexp']

        submission = np.array([[location, float(years)]])
        submission[:,0] = le_location.transform(submission[:,0])
        submission = submission.astype(float)

        linpredict = linear_predict.predict(submission).flat[0]
        decpredict = decision_predict.predict(submission).flat[0]

        roundlpredict = int(math.ceil(linpredict/1000) * 1000)
        rounddecpredict = int(math.ceil(decpredict/1000) * 1000)

        return render_template('results.html', linear = str(roundlpredict), decision = str(rounddecpredict))

    else:
        return render_template('predict.html')


@application.route('/forum', methods = ['POST', 'GET'])
@login_required
def forum():

    posts = Posts.query.order_by(Posts.PostID).all()
    users = users = User.query.order_by(User.id).all()
    idname = {}
    for user in users:
        idname[user.id] = user.name
    return render_template('forum.html', posts = posts, idname = idname)

@application.route('/post', methods=['POST', 'GET'])
def post():


    if request.method == 'POST':

        new_company = request.form['company']
        new_base_salary = request.form['base_salary']
        new_bonus_salary = request.form['bonus_salary']

        if (new_base_salary.isnumeric() == False):
            return "Base Salary must be an integer"
        
        if (new_bonus_salary.isnumeric() == False):
            return "Bonus Salary must be an integer"

        new_post = Posts(id = current_user.id, company = new_company, base_salary = int(new_base_salary), bonus_salary = int(new_bonus_salary), date_posted = date.today())

        db.session.add(new_post)
        db.session.commit()
        
        return redirect(url_for('forum'))

    return render_template('post.html')

@application.route('/logout', methods = ['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@application.route('/admin', methods = ['POST', 'GET'])
@login_required
def admin():
    id = current_user.id
    if (id == 1):
        users = User.query.order_by(User.id).all()
        return render_template('admin.html', users = users[1:])
    else:
        return "Not authorized"

@application.route('/delete/<int:id>')
def delete(id):

    if (id == 1):
        return "Cannot Delete"

    user_to_delete = User.query.get_or_404(id)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for('admin'))
    except:
        return 'There was a problem deleting the user'

if __name__ == "__main__":
    application.run(debug=True)