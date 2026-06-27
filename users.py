from flask import Blueprint, request, make_response, render_template, flash, redirect, url_for
from google.cloud import datastore
from json2html import *
from string import ascii_letters, digits
import json
import constants
import requests
from goal_convert import goal_convert

client = datastore.Client()

bp = Blueprint('users', __name__, template_folder='templates', static_folder='static', url_prefix='/home')


# Change route so that it is passing the id in it

@bp.route('/<uid>', methods=['POST', 'GET'])
def home(uid):
    # user_id = request.args.get("id")
    active = []
    completed = []
    url = request.root_url + "home/" + uid
    method = request.form.to_dict()
    challenges_completed = 0

    # Checks if user with user_id exists
    query = client.key(constants.users, int(uid))
    users = client.get(key=query)

    if not users:
        err = json.dumps({"Error": "No user with this user_id exists"})
        res = make_response(json2html.convert(json=err))
        res.headers.set('Content-Type', 'application/json')
        res.status_code = 404
        return res

    user_name = {"id": users.id, "name": str(users["first_name"] + " " + users["last_name"])}

    if request.method == 'GET':
        # Search for a challenge
        if request.args.get('search'):
            user_input = request.args['input'].lower()

            if user_input != '':
                # Query for all challenges that have a certain key word or key words -- Active, Favorite and Completed
                pass
            else:
                # Query for all challenges -- Active, Favorite and Completed
                pass

        if not request.args.get('search'):
            query = client.query(kind=constants.challenges)
            challenges = list(query.fetch())

            user_key = client.key(constants.users, int(uid))
            user = client.get(key=user_key)

            for each in user["challenges"]:
                # Looping for active challenges
                if each["completed"] is False:
                    for x in challenges:
                        if str(x.id) == str(each["challenge_id"]):
                            active.append((x.id, x["name"]))
                            break

                # Looping for completed challenges
                if each["completed"] is True:
                    for x in challenges:
                        if str(x.id) == str(each["challenge_id"]):
                            completed.append((x.id, x["name"]))
                            challenges_completed += 1

            res = make_response(
                render_template('userhome.html', user_name=user_name, challenges_completed=challenges_completed, completed=completed, active=active))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 200
            return res

    if request.method == "POST":
        cid = str(request.form['id'])
        user_key = client.key(constants.users, int(uid))
        user = client.get(key=user_key)

        ind = 0
        for challenge_id in user["challenges"]:
            if challenge_id['challenge_id'] == cid:
                del user["challenges"][ind]
                client.put(user)
                user["challenges"].append({"challenge_id": cid, "completed": True})
                client.put(user)
            ind += 1

        return redirect(url)

    else:
        # Status code 405
        res = make_response()
        res.headers.set('Allow', 'GET, POST')
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 405
        return res


@bp.route('/<uid>/challenge', methods=['POST', 'GET'])
def create_challenge(uid):
    if request.method == 'POST':
        res_content = request.form.to_dict()
        goal_list = request.form.getlist('goals[]')
        content = goal_convert(res_content, goal_list)

        # Check contents of the json file to make sure keys have values, and it is not empty.
        # Only supported attributes will be used. Any additional ones will be ignored.
        if not content or "name" not in content or "exercise_type" not in content or "duration" not in content \
                or "time_unit" not in content or "goals" not in content or "description" not in \
                content or "tags" not in content:
            err = json.dumps({"Error 400": "The request object is missing at least one of the required attributes"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 400
            return res

        # Check value of contents to make sure they are not null or have valid characters.
        if set(content["name"]).difference(ascii_letters + digits + " ") or \
                not isinstance(int(content["duration"]), int):
            err = json.dumps({"Error 400": "Your name of your Challenge has an invalid character"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 400
            return res

        exe_flag = False
        query = client.query(kind=constants.exercises)
        exercise_list = list(query.fetch())

        for exercise in exercise_list:
            if exercise["name"] == content["exercise_type"]:
                exe_flag = True

        if not exe_flag:
            url = url_for("exercises.exercises_post_get", _external=True)
            data = {
                "name": content["exercise_type"]
            }
            requests.post(url, json=json.dumps(data))

        exe_flag = False
        query = client.query(kind=constants.tags)
        tag_list = list(query.fetch())

        for tag in tag_list:
            if tag["name"] == content["tags"]:
                exe_flag = True

        if not exe_flag:
            url = url_for("tags.tags_post_get", _external=True)
            data = {
                "name": content["tags"]
            }
            requests.post(url, json=json.dumps(data))

        # Name of challenges must be unique
        query = client.query(kind=constants.challenges)
        challenges_list = list(query.fetch())

        # Search all challenges objects and compare the names to make sure they are unique
        for curr_challenges in challenges_list:
            if curr_challenges["name"] == content["name"]:
                err = json.dumps({"Error 403": "There is already a challenges with that name"})
                res = make_response(json2html.convert(json=err))
                res.headers.set('Content-Type', 'text/html')
                res.status_code = 403
                return res

        # Create new challenges entity
        new_challenges = datastore.entity.Entity(key=client.key(constants.challenges))
        new_challenges.update({"name": content["name"], "exercise_type": content["exercise_type"],
                               "duration": int(content["duration"]), "time_unit": content["time_unit"],
                               "goals": content["goals"], "description": content[
                "description"], "tags": content["tags"], "owner": uid})

        client.put(new_challenges)
        flash('Challenge created successfully!')
        url = request.root_url + "challenges/" + uid

        # Need to figure out how to work flash again, so that we can use for edits as well to tell user action is
        # forbidden.
        # flash('Challenge created successfully!')
        return redirect(url)

    elif request.method == "GET":

        query = client.key(constants.users, int(uid))
        users = client.get(key=query)
        user_name = {"id": users.id, "name": str(users["first_name"] + " " + users["last_name"])}

        url = url_for("exercises.exercises_post_get", _external=True)
        r = requests.get(url)
        exercises = r.json()

        url = url_for("tags.tags_post_get", _external=True)
        r = requests.get(url)
        tags = r.json()

        return render_template("create.html", exercises=exercises, user_name=user_name, tags=tags)


# This is to grab all the user's challenges and to create relationship between user and challenge.
@bp.route('/<uid>/challenges/<cid>', methods=["GET", "POST"])
def get_reservations(cid, uid):
    if 'application/json' not in request.accept_mimetypes:
        # Checks if client accepts json, if not return 406
        err = {"Error": "The request header ‘Accept' is not application/json"}
        res = make_response(err)
        res.headers.set('Content-Type', 'application/json')
        res.status_code = 406
        return res

    method = request.form.to_dict()
    url = request.root_url + "challenges/" + uid


    # Return json object that will be passed into the userhome.html
    if request.method == 'GET':
        query = client.key(constants.users, int(uid))
        users = client.get(key=query)
        user_name = {"id": users.id, "name": str(users["first_name"] + " " + users["last_name"])}

        url = url_for("exercises.exercises_post_get", _external=True)
        r = requests.get(url)
        exercises = r.json()

        url = url_for("tags.tags_post_get", _external=True)
        r = requests.get(url)
        tags = r.json()

        challenge_key = client.key(constants.challenges, int(cid))
        challenge = client.get(key=challenge_key)

        # Check if challenge exists
        if not challenge:
            return {"Error": "No challenge with this challenge_id exists"}, 404

        challenge["goals"] = challenge["goals"].split(",")
        challenge["tags"] = challenge["tags"].capitalize()
        return render_template("edit.html", exercises=exercises, user_name=user_name, tags=tags, content=challenge)

    elif method["_METHOD"] == "PUT":
        user_key = client.key(constants.users, int(uid))
        user = client.get(key=user_key)

        ind = 0
        for challenge_id in user["challenges"]:
            if challenge_id['challenge_id'] == cid:
                del user["challenges"][ind]
                client.put(user)
                flash('Left the challenge!')

                return redirect(url)
            ind += 1

        user["challenges"].append({"challenge_id": cid, "completed": False})
        client.put(user)
        flash('Challenge joined!')

        return redirect(url)

    elif method["_METHOD"] == "PATCH":

        res_content = request.form.to_dict()
        goal_list = request.form.getlist('goals[]')
        content = goal_convert(res_content, goal_list)

        challenge_key = client.key(constants.challenges, int(cid))
        challenge = client.get(key=challenge_key)

        # Checks if challenge with challenge_id exists
        if not challenge:

            err = json.dumps({"Error": "No challenge with this challenge_id exists"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 404
            return res

        elif challenge["owner"] != uid:
            err = json.dumps({"Error": "The challenge is owned by another user"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 401
            return res

        # Check value of contents to make sure they are not null or have valid characters.
        if set(content["name"]).difference(ascii_letters + digits + " "):
            err = json.dumps({"Error": "The request object has at least one invalid value assigned to an "
                                       "attribute"})
            res = make_response(json2html.convert(json=err))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 400
            return res

        # Name of challenge must be unique
        query = client.query(kind=constants.challenges)
        challenge_list = list(query.fetch())

        # Search all challenge objects and compare the names to make sure they are unique
        for curr_chllng in challenge_list:
            if curr_chllng["name"] == content["name"]:
                err = json.dumps({"Error": "There is already a challenge with that name"})
                res = make_response(json2html.convert(json=err))
                res.headers.set('Content-Type', 'text/html')
                res.status_code = 403
                return res

            # Unique challenge name
            challenge.update({"name": content["name"]})

        challenge.update({"exercise_type": content["exercise_type"],
                          "duration": int(content["duration"]), "time_unit": content["time_unit"],
                          "goals": content["goals"], "description": content[
                "description"], "tags": content["tags"], "owner": uid})

        client.put(challenge)

        flash('Challenge edited successfully!')

        return redirect(url)

    else:
        # Status code 405
        res = make_response()
        res.headers.set('Allow', 'GET, POST')
        res.headers.set('Content-Type', 'text/html')
        res.status_code = 405
        return res
