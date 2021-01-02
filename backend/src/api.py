import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES


@app.route('/drinks', methods=["GET"])
def get_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        formatted_drinks = [drink.short() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': formatted_drinks,
        })
    except:
        abort(500)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
'''


@app.route('/drinks-detail', methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):

    try:
        drinks = Drink.query.order_by(Drink.id).all()
        formatted_drinks = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': formatted_drinks,
        })
    except:
        abort(500)


'''
@TODO implement endpoint
    POST /drinks
        it should require the 'post:drinks' permission
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def create_drink(jwt):
    data = request.get_json()

    drink_title = data.get('title', None)
    drink_recipe = json.dumps(data.get('recipe', None))
    if drink_title == '' or len(drink_recipe) == 0:
        abort(422)
    try:
        drink = Drink(title=drink_title, recipe=drink_recipe)
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': drink.long(),
        })
    except:
        abort(500)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        it should require the 'patch:drinks' permission
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):
    data = request.get_json()
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        if 'title' in data:
            drink.title = data.get('title')
        if 'recipe' in data:
            drink.recipe = json.dumps(data.get('recipe', None))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()],
        })
    except:
        abort(500)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should require the 'delete:drinks' permission
'''


@app.route('/drinks/<drink_id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id,
        })
    except:
        abort(500)


## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "not authorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500
