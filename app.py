from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "justarandomsecretkeypassingby"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
app.config['SQLALCHEMY_BINDS'] = {
    'data': 'sqlite:///db/data',
    'user': 'sqlite:///db/user'
}
db = SQLAlchemy(app)
Bootstrap(app)


class User(db.Model):
    __bind_key__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

    def __repr__(self):
        return '<User %r>' % self.id


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


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                return redirect(url_for('routes.dashboard'))

        return '<h1> Invalid username or password </h1>'
        # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return render_template('login.html', form=form)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return '<h1> New user was created </h1>'
        # return '<h1>' + form.username.data + ' ' + form.email.data + form.password.data + '</h1>'

    return render_template('signup.html', form=form)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap


@app.route('/', methods=['POST', 'GET'])
def index():
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

        return render_template('index.html', properties=properties, cities=cities)
    else:
        cities = []
        # city = 'Paris'
        for property in RealEstate.query.distinct(RealEstate.city):
            cities.append(property.city)
        # properties = RealEstate.query.order_by(RealEstate.date_created).filter(RealEstate.city == city).all()
        return render_template("index.html", properties=[], cities=cities)


@app.route('/delete/<int:id>')
def delete(id):
    property_to_delete = RealEstate.query.get_or_404(id)
    try:
        db.session.delete(property_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Issue when deleting'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    property = RealEstate.query.get_or_404(id)

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


if __name__ == '__main__':
    app.run(debug=True)
