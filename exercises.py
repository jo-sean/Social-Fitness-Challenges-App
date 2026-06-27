from flask import Blueprint, request, make_response, render_template  # , url_for, flash, redirect, jsonify
from string import ascii_letters, digits
from google.cloud import datastore
import constants
import json
# from json2html import *
# from check_jwt import check_jwt

client = datastore.Client()

bp = Blueprint('exercises', __name__, url_prefix='/exercises')


@bp.route('', methods=['POST', 'GET'])
def exercises_post_get():

    if request.method == 'GET':
        query = client.query(kind=constants.exercises)
        exercises_iterator = query.fetch()
        total_challenges = list(exercises_iterator)
        output = {"exercises": total_challenges}

        res = make_response(json.dumps(output))
        res.mimetype = 'application/json'
        res.status_code = 200
        return res

    elif request.method == 'POST':
        content = json.loads(request.get_json())
        new_exercise = datastore.entity.Entity(key=client.key(constants.exercises))
        new_exercise.update({"name": content["name"]})
        client.put(new_exercise)

        res = make_response(json.dumps(new_exercise))
        res.mimetype = 'application/json'
        res.status_code = 200
        return res



