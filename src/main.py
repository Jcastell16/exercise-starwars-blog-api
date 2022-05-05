"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import requests
from flask import Flask, request, jsonify, url_for
from datetime import timedelta
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("FLASK_APP_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=3600)
MIGRATE = Migrate(app, db)
jwt = JWTManager(app)
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

## LOGIN ##
###########
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username is None or password is None:
        return jsonify({"msg": "Bad username or password"}), 401
    user = User.query.filter_by(username=username, password=password).first()
    if user is None:
        return jsonify({"error": "Invalid username or password."}), 401 
    elif user.password != password:
        return jsonify({"error": "User or password not found."}), 401
    else:
        create_token = create_access_token(identity=user.id)
    return jsonify({
        "user_id" : user.id,
        "username" : user.username,
        "token" : create_token
    })

## USERS ENDPOINT ##
####################

@app.route('/users', methods=['GET'])
@jwt_required()
def getUsers():
    users = User.query.all()
    request = list(map(lambda user:user.serialize(),users))    
    return jsonify(request), 200

@app.route("/users", methods=["POST"])
def register_user():
    name = request.json.get("name", None)
    username = request.json.get("username", None)
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if name is None:
        return jsonify({"msg": "Please provide a valid name."}), 400
    if username is None:
        return jsonify({"msg": "Please provide a valid username."}), 400
    if email is None:
        return jsonify({"msg": "Please provide a valid email."}), 400
    if password is None:
        return jsonify({"msg": "Please provide a valid password."}), 400
    
    user = User.query.filter_by(username=username, email=email, password=password).first()
    if user:
        return jsonify({"msg": "User already exists."}), 401
    else:
        new_user = User()
        new_user.name = name
        new_user.username = username
        new_user.email = email
        new_user.password = password

        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User account was successfully created."}), 200

#DELETE
@app.route('/users', methods=["DELETE"])
@jwt_required()
def delete_user():
    current_user = get_jwt_identity()
    userdel = User.query.get(current_user)
    if userdel is None:
        return jsonify({"msg": "The user does not exist!."}), 404
    db.session.delete(userdel)
    db.session.commit()
    return jsonify({"Proccess completed by"}),200

## CHARACTER ##
###############

@app.route('/characters', methods=['GET'])
def getCharacters():
    characters = Character.query.all()
    request = list(map(lambda character:character.serialize(),characters))    
    return jsonify(request), 200

@app.route('/characters/<int:character_id>', methods=['GET'])
def getCharacter(character_id):
    if character_id is None:
        return jsonify({"msg": "The user does not exist!."}), 404
    character = Character.query.filter_by(id=character_id).first()
    request = character.serialize()
    return jsonify(request), 200

@app.route("/characters", methods=["POST"])
def register_characters():
    name = request.json.get("name", None)
    birth_year = request.json.get("birth_year", None)
    gender = request.json.get("gender", None)
    height = request.json.get("height", None)
    mass = request.json.get("mass", None)
    skin_color = request.json.get("skin_color", None)
    eye_color = request.json.get("eye_color", None)
    hair_color = request.json.get("hair_color", None)

    if name is None:
        return jsonify({"msg": "Please provide a valid name."}), 400
    if birth_year is None:
        return jsonify({"msg": "Please provide a valid Birth Year."}), 400
    if gender is None:
        return jsonify({"msg": "Please provide a valid Gender."}), 400
    if height is None:
        return jsonify({"msg": "Please provide a valid Height."}), 400
    if mass is None:
        return jsonify({"msg": "Please provide a valid Mass."}), 400
    if skin_color is None:
        return jsonify({"msg": "Please provide a valid Skin Color."}), 400
    if eye_color is None:
        return jsonify({"msg": "Please provide a valid Eye Color."}), 400
    if hair_color is None:
        return jsonify({"msg": "Please provide a valid Hair Color."}), 400
    
    character = Character.query.filter_by(name=name).first()
    if character:
        return jsonify({"msg": "User already exists."}), 401
    else:
        new_character = Character()
        new_character.name = name
        new_character.birth_year = birth_year
        new_character.gender = gender
        new_character.height = height
        new_character.mass = mass
        new_character.skin_color = skin_color
        new_character.eye_color = eye_color
        new_character.hair_color = hair_color

        db.session.add(new_character)
        db.session.commit()
        return jsonify({"msg": "User account was successfully created."}), 200

## PLANET ##
############

@app.route('/planets', methods=['GET'])
def getPlanets():
    planets = Planet.query.all()
    request = list(map(lambda planet:planet.serialize(),planets))    
    return jsonify(request), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def getplanet(planet_id):
    if planet_id is None:
        return jsonify({"msg": "The user does not exist!."}), 404
    planet = Planet.query.filter_by(id=planet_id).first()
    request = planet.serialize()
    return jsonify(request), 200

# POST
@app.route("/planets", methods=["POST"])
def register_planet():
    name = request.json.get("name", None)
    rotation_period = request.json.get("rotation_period", None)
    orbital_period = request.json.get("orbital_period", None)
    diameter = request.json.get("diameter", None)
    climate = request.json.get("climate", None)
    gravity = request.json.get("gravity", None)
    terrain = request.json.get("terrain", None)
    surface_water = request.json.get("surface_water", None)
    population = request.json.get("population", None)
    
    
    if name is None:
        return jsonify({"msg": "Please provide a valid name."}), 400
    if rotation_period is None:
        return jsonify({"msg": "Please provide a valid Rotation Period."}), 400
    if orbital_period is None:
        return jsonify({"msg": "Please provide a valid Orbital Period."}), 400
    if diameter is None:
        return jsonify({"msg": "Please provide a valid Diameter."}), 400
    if climate is None:
        return jsonify({"msg": "Please provide a valid Climate."}), 400
    if gravity is None:
        return jsonify({"msg": "Please provide a valid Gravity."}), 400
    if terrain is None:
        return jsonify({"msg": "Please provide a valid Terrain."}), 400
    if surface_water is None:
        return jsonify({"msg": "Please provide a valid Surface Water."}), 400
    if population is None:
        return jsonify({"msg": "Please provide a valid Population."}), 400
    
    planet = Planet.query.filter_by(name=name).first()
    if planet:
        return jsonify({"msg": "User already exists."}), 401
    else:
        new_planet = Planet()
        new_planet.name = name
        new_planet.rotation_period = rotation_period
        new_planet.orbital_period = orbital_period
        new_planet.diameter = diameter
        new_planet.climate = climate
        new_planet.gravity = gravity
        new_planet.terrain = terrain
        new_planet.surface_water = surface_water
        new_planet.population = population

        db.session.add(new_planet)
        db.session.commit()
        return jsonify({"msg": "User account was successfully created."}), 200

## FAVORITE ##
##############

@app.route('/users/favorites', methods=['GET'])
@jwt_required()
def getFavorites():
    current_user = get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=current_user).all()
    all_favorites = list(map(lambda all:all.serialize(),favorites))  
    return jsonify(all_favorites), 200

@app.route('/favorite/character/<int:character_id>', methods=["POST"])
@jwt_required()
def favorite_character(character_id):   
    if character_id is None:
        return jsonify({"msg": "Please provide a valid Character."}), 400
    fav_character = Favorite.query.filter_by(character_id=character_id).first()
    if fav_character:
        return jsonify({"msg": "User already exists."}), 401
    else:
        current_user = get_jwt_identity()
        new_favorite = Favorite()
        new_favorite.character_id = character_id
        new_favorite.user_id = current_user
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"msg": "Favorite was successfully created."}), 200

@app.route('/favorite/planet/<int:planet_id>', methods=["POST"])
@jwt_required()
def favorite_planet(planet_id):   
    if planet_id is None:
        return jsonify({"msg": "Please provide a valid Planet."}), 400
    fav_planet = Favorite.query.filter_by(planet_id=planet_id).first()
    if fav_planet:
        return jsonify({"msg": "User already exists."}), 401
    else:
        current_user = get_jwt_identity()
        new_favorite = Favorite()
        new_favorite.planet_id = planet_id
        new_favorite.user_id = current_user
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"msg": "Favorite was successfully created."}), 200

@app.route('/favorite/character/<int:character_id>', methods=["DELETE"])
@jwt_required()
def favorite_character_delete(character_id):   
    if character_id is None:
        return jsonify({"msg": "Please provide a valid Character."}), 400
    current_user = get_jwt_identity()
    del_character = Favorite.query.filter_by(character_id=character_id, user_id=current_user).first()
    if del_character is None:
        return jsonify({"msg": "The Favorite Character does not exist!."}), 401
    db.session.delete(del_character)
    db.session.commit()
    return jsonify({"msg": "Favorite was successfully delete."}), 200

@app.route('/favorite/planet/<int:planet_id>', methods=["DELETE"])
@jwt_required()
def favorite_planet_delete(planet_id):   
    if planet_id is None:
        return jsonify({"msg": "Please provide a valid Planet."}), 400
    current_user = get_jwt_identity()
    del_planet = Favorite.query.filter_by(planet_id=planet_id, user_id=current_user).first()
    if del_planet is None:
        return jsonify({"msg": "The Favorite Character does not exist!."}), 401
    db.session.delete(del_planet)
    db.session.commit()
    return jsonify({"msg": "Favorite was successfully delete."}), 200

## MIGRATE DATABASE ##
######################

BASE_URL = "https://www.swapi.tech/api"
@app.route('/population/characters', methods=['POST'])
def population_character():
    #Solicitud de las caracteristicas
    response = requests.get(f"{BASE_URL}/{'people'}/?page=1&limit=20")
    response = response.json()
    all_results = []

    for result in response['results']:
        detail = requests.get(result['url'])
        detail = detail.json()
        all_results.append(detail['result']['properties'])

    instances = []

    for character in all_results:
        instance = Character.create(character)
        instances.append(instance)
    return jsonify(list(map(lambda inst: inst.serialize(), instances))), 200

URL_BASE = "https://www.swapi.tech/api"
@app.route('/population/planets', methods=['POST'])
def handle_characters():
    response = requests.get(f"{URL_BASE}/planets/?page=2&limit=100",)
    response = response.json()
    all_results = []

    for result in response['results']:
        detail = requests.get(result['url'])
        detail = detail.json()
        all_results.append(detail)
    
    instances = []  

    for planet in all_results:
        instance = Planet.create(planet)
        instances.append(instance)
    return jsonify(list(map(lambda inst: inst.serialize(), instances))), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
