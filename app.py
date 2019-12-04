from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "justarandomsecretkeypassingby"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
app.config['SQLALCHEMY_BINDS'] = {
    'data': 'sqlite:///db/data',
    'user': 'sqlite:///db/user'
}
db = SQLAlchemy(app)
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    __bind_key__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


class RealEstate(db.Model):
    __bind_key__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    landlord = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Property %r>' % self.id


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=40)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('email ', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=40)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect('/')
        return render_template('mistake.html', error_message="Invalid username or password")
        # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return render_template('login.html', form=form)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter(or_(User.username == form.username.data, User.email==form.email.data)).all()
        if len(user) > 0:
            return render_template('mistake.html', error_message="There is already a user with this username or email address")
        else:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return render_template('mistake.html', error_message="New user was created")

    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/', methods=['POST', 'GET'])
def index():
    authenticated = current_user.is_authenticated
    if authenticated:
        name = current_user.username
    else:
        name = "***usernotloggedin***"

    if request.method == 'POST':
        property_name = request.form['name']
        property_description = request.form['description']
        property_rooms = request.form['rooms']
        property_landlord = request.form['landlord']
        property_city = request.form['city']
        new_property = RealEstate(name=property_name,
                                  description=property_description,
                                  rooms=property_rooms,
                                  landlord=property_landlord,
                                  city=property_city
                                  )
        try:
            db.session.add(new_property)
            db.session.commit()
            return redirect('/')
        except:
            return "Issue adding the property"
    if request.method == "GET":
        cities = []
        for property in RealEstate.query.distinct(RealEstate.city):
            if property.city not in cities:
                cities.append(property.city)
        city = request.args.get('city')
        properties = RealEstate.query.order_by(RealEstate.date_created).filter(RealEstate.city == city).all()
        return render_template('index.html', properties=properties, cities=cities, name=name,
                               authenticated=authenticated)
    else:
        cities = []
        for property in RealEstate.query.distinct(RealEstate.city):
            cities.append(property.city)
        return render_template("index.html", properties=[], cities=cities, name=current_user.username,
                               authenticated=authenticated)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    name = current_user.username
    property_to_delete = RealEstate.query.get_or_404(id)

    if property_to_delete.landlord == name:
        try:
            db.session.delete(property_to_delete)
            db.session.commit()
            return redirect('/')
        except:
            return 'Issue when deleting'
    else:
        return render_template('mistake.html', error_message="You can't delete someone else's property")


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    property = RealEstate.query.get_or_404(id)
    name = current_user.username
    if property.landlord == name:
        if request.method == 'POST':
            property.name = request.form['name']
            property.description = request.form['description']
            property.rooms = request.form['rooms']
            property.landlord = request.form['landlord']
            property.city = request.form['city']
            try:
                db.session.commit()
                return redirect('/')
            except:
                return "Error when updating"
        else:
            return render_template('update.html', property=property)
    else:
        return render_template('mistake.html', error_message="You can't edit someone else's property")


if __name__ == '__main__':
    app.run(debug=True)
