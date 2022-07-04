from flask import Flask, render_template, url_for, request, redirect
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


application = Flask(__name__)
db = SQLAlchemy(application)
bcrypt = Bcrypt(application)
ENV = 'dev'

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

    id = db.Column(db.INT, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)


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
                return redirect(url_for('dash'))

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


@application.route('/dash', methods=['POST', 'GET'])
@login_required
def dash():

    if request.method == 'POST':
        location = request.form['location']
        
        if (location == "Default"):
            return render_template('dash.html')
        years = request.form['yearsofexp']

        submission = np.array([[location, float(years)]])
        submission[:,0] = le_location.transform(submission[:,0])
        submission = submission.astype(float)

        linpredict = linear_predict.predict(submission).flat[0]
        decpredict = decision_predict.predict(submission).flat[0]

        roundlpredict = int(math.ceil(linpredict/1000) * 1000)
        rounddecpredict = int(math.ceil(decpredict/1000) * 1000)

        return render_template('predict.html', linear = str(roundlpredict), decision = str(rounddecpredict))

    else:
        return render_template('dash.html')


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
    application.run(debug = True)