from flask import Flask, render_template, request
import badges
import users
import challenges
import exercises
import auth
import tags

app = Flask(__name__)

app = Flask(__name__)
app.secret_key = "tAkdK6Aj6X5^649&h0jg$"
app.register_blueprint(challenges.bp)
app.register_blueprint(users.bp)
app.register_blueprint(badges.bp)
app.register_blueprint(exercises.bp)
app.register_blueprint(auth.auth)
app.register_blueprint(tags.bp)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
