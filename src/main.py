"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    user = User.query.all()
    all_user = list(map(lambda x: x.serialize(),user))

    return jsonify(all_user), 200


@app.route('/people', methods=['GET'])
def handle_all_people():

    people = People.query.all()
    all_people = list(map(lambda x: x.serialize(),people))
    # response_body = {
    #     "msg": "Hello, this is your GET /user response "
    # }

    return jsonify(all_people), 200

@app.route('/people/<int:person_id>', methods=['GET'])
def handle_people(person_id):

    person = People.query.get(person_id)
    return jsonify(person.serialize()), 200



@app.route('/planet', methods=['GET'])
def handle_all_planet():

    planet = Planet.query.all()
    all_planet = list(map(lambda x: x.serialize(),planet))
    # response_body = {
    #     "msg": "Hello, this is your GET /user response "
    # }

    return jsonify(all_planet), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def handle_planet(planet_id):

    planet = Planet.query.get(planet_id)
    return jsonify(planet.serialize()), 200


#favorites
@app.route('/user/<int:user_id>/favorite', methods=['GET'])
def get_fav(user_id):
    query = User.query.get(user_id)
    if query is None:
        return('El usuario no tiene favoritos agregados')
    else:
        result = Favorite.query.filter_by(user_id= query.id)
        fav_list = list(map(lambda x: x.serialize(), result))
        return jsonify(fav_list), 200


@app.route('/user/<int:user_id>/favorite', methods=['POST'])
def add_fav(user_id):

    body = request.get_json() 
    # return body
    
    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)

    idPeople = body["idPeople"]
    idPlanet = body["idPlanet"]

    newFavorite = Favorite(user_id=user_id,people_id = idPeople,planet_id = idPlanet) 
    db.session.add(newFavorite)
    db.session.commit()
    return {"mensaje":"registrado correctamente"}, 200

#favorite delete
@app.route('/favorite/<int:favorite_id>', methods=['DELETE'])
def delete_fav(favorite_id):
    query = Favorite.query.get(favorite_id)

    if query is None:
        return ({"mensaje":'El favorito no existe'}),300
    else:
        db.session.delete(query)
        db.session.commit()
        return {"mensaje":"eliminado correctamente"}, 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
