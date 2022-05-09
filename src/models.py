from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()

## USER ##
##########

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    favorite = db.relationship("Favorite", backref="user", uselist=True)

    def __repr__(self):
        return '<User: %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email
            # do not serialize the password, its a security breach
        }

## FAVORITE ##
##############

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(60), nullable=False)
    nature = db.Column(db.String(50), nullable=False)
    nature_id = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint(
    'user_id',
    'name',
    name="dont_repeat_favorites"
    ),)

    def __repr__(self):
        return f"<Favorites object {self.id}>"

    def serialize(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "nature": self.nature,
            "nature_id": self.nature_id
        }

## ITEMS ADD ##
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    birth_year = db.Column(db.String(25), nullable=False)
    gender = db.Column(db.String(25), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    mass = db.Column(db.Integer, nullable=False)
    skin_color = db.Column(db.String(25), nullable=False)
    eye_color = db.Column(db.String(25), nullable=False)
    hair_color = db.Column(db.String(25), nullable=False)

    def serialize(self):
        return{
            "id" : self.id,
            "name" : self.name,
            "birth_year" : self.birth_year,
            "gender" : self.gender,
            "height" : self.height,
            "mass" : self.mass,
            "skin_color" : self.skin_color,
            "eye_color" : self.eye_color,
            "hair_color" : self.hair_color
        }
    
    def __repr__(self):
        return '<Character: %r>' % self.name
        
    def __init__(self, *args, **kwargs):

        for (key, value) in kwargs.items():
            if hasattr(self, key):
                attr_type = getattr(self.__class__, key).type

                try:
                    attr_type.python_type(value)
                    setattr(self, key, value)
                except Exception as error:
                    print(f"ignore the other values: {error.args}")

    @classmethod
    def create(cls, data):
        instance = cls(**data)
        if (not isinstance(instance, cls)):
            print("Something failed")
            return None
        db.session.add(instance)
        try:
            db.session.commit()
            print(f"Created: {instance.name}")
            return instance
        except Exception as error:
            db.session.rollback()
            print(error.args)


class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    diameter = db.Column(db.Integer, nullable=False)
    gravity = db.Column(db.String(50), nullable=False)
    terrain = db.Column(db.String(50), nullable=False)
    surface_water = db.Column(db.String(50), nullable=False)
    population = db.Column(db.Integer, nullable=False)
    rotation_period = db.Column(db.Integer, nullable=False)
    orbital_period = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return{
            "id" : self.id,
            "name" : self.name,
            "diameter" : self.diameter,
            "gravity" : self.gravity,
            "terrain" : self.terrain,
            "surface_water" : self.surface_water,
            "population" : self.population,
            "rotation_period" : self.rotation_period,
            "orbital_period" : self.orbital_period
        }

    def __repr__(self):
        return '<Planet: %r>' % self.name
    
    def __init__(self, *args, **kwargs):

        for (key, value) in kwargs.items():
            if hasattr(self, key):
                attr_type = getattr(self.__class__, key).type

                try:
                    attr_type.python_type(value)
                    setattr(self, key, value)
                except Exception as error:
                    print(f"ignore the other values: {error.args}")

    @classmethod
    def create(cls, data):
        instance = cls(**data)
        if (not isinstance(instance, cls)):
            print("Something failed")
            return None
        db.session.add(instance)
        try:
            db.session.commit()
            print(f"Created: {instance.name}")
            return instance
        except Exception as error:
            db.session.rollback()
            print(error.args)