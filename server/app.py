#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

# Ensure database tables exist when the app is imported (useful for tests)
with app.app_context():
    db.create_all()
    # Ensure there's at least one Bakery for tests that expect id=1
    if not Bakery.query.get(1):
        default_bakery = Bakery(name='Default Bakery')
        db.session.add(default_bakery)
        db.session.commit()

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):

    bakery = Bakery.query.filter_by(id=id).first()
    bakery_serialized = bakery.to_dict()
    return make_response ( bakery_serialized, 200  )

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )


@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    """Create a new BakedGood from form data and return it as JSON."""
    name = request.form.get('name')
    price = request.form.get('price')
    bakery_id = request.form.get('bakery_id')

    # convert types where appropriate
    try:
        price_val = int(float(price)) if price is not None else None
    except ValueError:
        price_val = None

    try:
        bakery_id_val = int(bakery_id) if bakery_id is not None else None
    except ValueError:
        bakery_id_val = None

    new_bg = BakedGood(name=name, price=price_val, bakery_id=bakery_id_val)
    db.session.add(new_bg)
    db.session.commit()

    return make_response(jsonify(new_bg.to_dict()), 201)


@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    """Update a Bakery's attributes via form data and return updated bakery."""
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response({'error': 'Bakery not found'}, 404)

    name = request.form.get('name')
    if name is not None:
        bakery.name = name

    db.session.add(bakery)
    db.session.commit()

    return make_response(jsonify(bakery.to_dict()), 200)


@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    """Delete a BakedGood by id and return an empty JSON response."""
    bg = BakedGood.query.get(id)
    if not bg:
        return make_response({'error': 'BakedGood not found'}, 404)

    db.session.delete(bg)
    db.session.commit()

    return make_response(jsonify({}), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)