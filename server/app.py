#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch=True)


db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class AllRestaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        restaurant_list = [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]
        return make_response(restaurant_list, 200)

api.add_resource(AllRestaurants, '/restaurants')


class OneRestaurant(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if(not restaurant):
            return make_response({"error": "Restaurant not found"}, 404)
        return make_response(restaurant.to_dict(only=('id', 'name', 'address', 'restaurant_pizzas')), 200)
    

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)

        db.session.delete(restaurant)
        db.session.commit()
        return make_response({}, 204)

api.add_resource(OneRestaurant, '/restaurants/<int:id>')


class AllPizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        pizza_list = [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas]
        return make_response(pizza_list, 200)

api.add_resource(AllPizzas, '/pizzas')


class CreateRestaurantPizza(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_rest_pizza= RestaurantPizza(price=data.get("price"), pizza_id=data.get("pizza_id"), restaurant_id=data.get("restaurant_id"))

            db.session.add(new_rest_pizza)
            db.session.commit()

            return make_response(new_rest_pizza.to_dict(), 201)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
  
api.add_resource(CreateRestaurantPizza, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
