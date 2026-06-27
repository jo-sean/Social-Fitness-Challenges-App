from flask import Blueprint, request, make_response, render_template
from google.cloud import datastore
import constants

client = datastore.Client()

bp = Blueprint('badges', __name__, url_prefix='/badges')

@bp.route('/<uid>', methods=['GET'])
def get_badges(uid):

    query = client.query(kind=constants.users)
    users = list(query.fetch())

    query1 = client.query(kind=constants.challenges)
    challenges = list(query1.fetch())

    badge_dict = {}
    for user in users:
        user_name = str(user["first_name"] + " " + user["last_name"])
        badge_dict[user_name] = 0

        for each in user["challenges"]:
            if each["completed"] is True:
                for x in challenges:
                    if str(x.id) == str(each["challenge_id"]):
                        badge_dict[user_name] += 1

    for account in badge_dict.items():
        if account[1] > 0:
            print(account[0])

    return render_template("badges.html", badge_dict = badge_dict, uid=uid)
