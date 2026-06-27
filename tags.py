from flask import Blueprint, request, make_response, render_template  # , url_for, flash, redirect, jsonify
from string import ascii_letters, digits
from google.cloud import datastore
import constants
import json
# from json2html import *
# from check_jwt import check_jwt

client = datastore.Client()

bp = Blueprint('tags', __name__, url_prefix='/tags')


@bp.route('', methods=['POST', 'GET'])
def tags_post_get():

    if request.method == 'GET':
        query = client.query(kind=constants.tags)
        exercises_iterator = query.fetch()
        total_challenges = list(exercises_iterator)
        output = {"tags": total_challenges}

        res = make_response(json.dumps(output))
        res.mimetype = 'application/json'
        res.status_code = 200
        return res

    elif request.method == 'POST':
        content = json.loads(request.get_json())
        print(content)
        new_tag = datastore.entity.Entity(key=client.key(constants.tags))
        new_tag.update({"name": content["name"]})
        client.put(new_tag)

        res = make_response(json.dumps(new_tag))
        res.mimetype = 'application/json'
        res.status_code = 200
        return res
      
