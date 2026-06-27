from flask import Blueprint, request, make_response, render_template  # , url_for, flash, redirect
from google.cloud import datastore
import constants
import json
from json2html import *

client = datastore.Client()

bp = Blueprint('challenges', __name__, url_prefix='/challenges')


@bp.route('/<uid>', methods=['GET'])
def challenges_get(uid):
    # Checks if JWT was provided in Authorization header
    # sub = check_jwt(request.headers)

    if request.method == 'GET':

        if ('*/*' or 'application/json') not in request.accept_mimetypes:
            # Checks if client accepts json, if not return 406
            err = json.dumps({"Error 406": "The request header ‘Accept' is not application/json"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 406
            return res

        # Reset the query to show the objects
        query = client.query(kind=constants.challenges)
        q_limit = int(request.args.get('limit', '10'))
        q_offset = int(request.args.get('offset', '0'))

        # Get result of query and make into a list
        challenges_iterator = query.fetch(limit=q_limit, offset=q_offset)
        pages = challenges_iterator.pages
        total_challenges = list(next(pages))

        # Create a "next" url page using
        if challenges_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None

        # Adds id key and value to each json slip; add next url
        for challenges in total_challenges:
            challenges["id"] = challenges.key.id
            challenges["self"] = request.base_url + "/" + str(challenges.key.id)
        output = {"challenges": total_challenges, "user": uid}

        if next_url:
            output["next"] = next_url

        if q_offset != 0:
            q_offset = q_offset - q_limit

        output["previous"] = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(q_offset)

        output["id"] = uid

        # code for which challenges are current, to show the user on 'participate'. 
        output["current_challenges"] = []
        user_query = client.query(kind=constants.users)
        user_accounts = list(user_query.fetch())
        for user_1 in user_accounts:
            if user_1.id == int(uid):
                current_challenges = user_1["challenges"]
                for challenge in current_challenges:
                        output["current_challenges"].append(int(challenge["challenge_id"]))
        print(output["current_challenges"])

        res = make_response(render_template("participate.html", content=output))
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 200
        return res

    else:
        # Status code 405
        res = make_response()
        res.headers.set('Allow', 'GET, POST')
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 405
        return res


@bp.route('/search', methods=['POST'])
def challenge_search():
    if request.method == 'POST':

        if ('*/*' or 'application/json') not in request.accept_mimetypes:
            # Checks if client accepts json, if not return 406
            err = json.dumps({"Error 406": "The request header ‘Accept' is not application/json"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 406
            return res

        content = request.form.to_dict()
        print(content)

        # Get the query to show the objects
        query = client.query(kind=constants.challenges)
        query.add_filter("tags", "=", content["tag"])

        # Get result of query and make into a list
        total_challenges = list(query.fetch())

        # Adds id key and value to each json slip; add next url
        for challenges in total_challenges:
            challenges["id"] = challenges.key.id

        output = {"challenges": total_challenges, "id": content["user_id"]}

        res = make_response(render_template("participate.html", content=output))
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 200
        return res

    else:
        # Status code 405
        res = make_response()
        res.headers.set('Allow', 'POST')
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 405
        return res


