from flask import Blueprint, jsonify
from .models import Restaurant, MenuItem
from sqlalchemy import text
from . import db
import json as pyjs

json = Blueprint('json', __name__)

#JSON APIs to view Restaurant Information

@json.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurant_menu_json(restaurant_id):
    # Input validation for restaurant_id
    if not isinstance(restaurant_id, int):
        return "Invalid restaurant_id parameter", 400

    # Parameterized query 
    query = text('select * from menu_item where restaurant_id = :restaurant_id')
    items = db.session.execute(query, {'restaurant_id': restaurant_id})
    items_list = [i._asdict() for i in items]
    return pyjs.dumps(items_list)


@json.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menu_item_json(restaurant_id, menu_id):
    # Input validation for restaurant_id
    if not isinstance(restaurant_id, int):
        return "Invalid restaurant_id parameter", 400

    # Input validation for menu_id
    if not isinstance(menu_id, int):
        return "Invalid menu_id parameter", 400

    # Parameterized query 
    query = text('select * from menu_item where id = :menu_id limit 1')
    menu_item = db.session.execute(query, {'menu_id': menu_id})
    items_list = [i._asdict() for i in menu_item]
    return pyjs.dumps(items_list)


@json.route('/restaurant/JSON')
def restaurants_json():
    # Parameterized query 
    query = text('select * from restaurant')
    restaurants = db.session.execute(query)
    rest_list = [r._asdict() for r in restaurants]
    return pyjs.dumps(rest_list)
