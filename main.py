from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class RealEstate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    landlord = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Property %r>' % self.id


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


if __name__ == "__main__":
    app.run(debug=True)
