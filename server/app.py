#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()

        try:
            user = User(
                username = json.get('username'),    
                image_url = json.get('image_url'),
                bio = json.get('bio')
            )
            user.password_hash = json['password']
    
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            return {"error": "Missing required fields"}, 422
    
class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return user.to_dict(), 200
        return {"error": "You messed up the check"}, 401

class Login(Resource):
    def post(self):
        json = request.get_json()
        user = User.query.filter(User.username == json['username']).first()

        if user:
            if user.authenticate(json['password']):
                session['username'] = json['username']
                session['user_id'] = user.id
                return user.to_dict()
        return {'error': 'login failure'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        else:
            return {'error': 'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            recipes = Recipe.query.all()
            return [recipe.to_dict() for recipe in recipes], 200
        else:
            return {"error": "Unauthorized"}, 401

    def post(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        json = request.get_json()

        if user:
            try:
                recipe = Recipe(
                    title=json['title'],
                    instructions=json['instructions'],
                    minutes_to_complete=json['minutes_to_complete'],
                    user_id=user.id
                )
                print('What')
                db.session.add(recipe)
                db.session.commit()
                return recipe.to_dict(), 201
            except IntegrityError:
                return {"error": "Missing required fields"}, 422
        else:
            return {"error": "Unauthorized"}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)