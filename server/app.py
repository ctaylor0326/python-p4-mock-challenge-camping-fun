#!/usr/bin/env python3

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'instance/app.db')}")

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Activity, Camper, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)


@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = [camper.to_dict(only=("id", "name", "age")) for camper in Camper.query.all()]
        return make_response(jsonify(campers), 200)
    
    def post(self):
        camper_json = request.get_json()
        try:
            camper = Camper(name=camper_json.get('name'), age=camper_json.get('age'))
            db.session.add(camper)
            db.session.commit()
            return make_response(jsonify(camper.to_dict(only=('id', 'name', 'age'))), 201)
        except ValueError:
            return make_response(jsonify({"error": "Validation failed."}), 400)
    

api.add_resource(Campers, '/campers')

class Activities(Resource):
    def get(self):
        activities = [activity.to_dict(only=("id", "name", "difficulty")) for activity in Activity.query.all()]
        return make_response(jsonify(activities), 200)

api.add_resource(Activities, '/activities')

class CamperByID(Resource):
    def get(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return make_response({"error": "404 Camper not found"}, 404)
        camper_dict = camper.to_dict()
        response = make_response(
            camper_dict, 200
        )
        return response
api.add_resource(CamperByID, '/campers/<int:id>')

class ActivitiesByID(Resource):
    def get(self, id):
        pass

    def delete(self, id):
        activity = Activity.query.get(id)
        if not activity:
            return make_response(jsonify({"error": "404: Activity not found"}), 404)
        db.session.delete(activity)
        db.session.commit()
        return {}, 204

api.add_resource(ActivitiesByID, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        signup_json = request.get_json()
        try:
            signup = Signup(activity_id=signup_json.get('activity_id'), camper_id=signup_json.get('camper_id'), time=signup_json.get('time'))
            db.session.add(signup)
            db.session.commit()
            return make_response(jsonify(signup.activity.to_dict(only=("id", "name", "difficulty"))), 201)
        except ValueError:
            return make_response(jsonify({"error": "Validation failed."}), 400)
        
api.add_resource(Signups, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
