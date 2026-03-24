import json
import random
import requests
from flask import Flask, render_template, request, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required, \
    AnonymousUserMixin
from sqlalchemy.util import NoneType
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

api_url = "https://restcountries.com/v3.1/"
country_names_json = json.loads(requests.get(api_url + 'all?fields=name').text)
country_names_list = []
for i in country_names_json:
    country_names_list.append(i['name']['common'])
country_names_list.sort()

win_score = 1000
hint_price = 100
max_hints = 9
max_rounds_amount = 9
max_guesses_amount = 3

possible_hints_list = {
    "a": "capital",
    "b": "continents",
    "c": "landlocked",
    "d": "population",
    "e": "area",  # in km^2
    "f": "independent",
    "g": "currencies",  # symbol and concat name ex: Canadian dollar -> dollar
    "h": "flags",
    "i": "coatOfArms",
    "j": "car",  # side of road
    "k": "idd",  # phone code + suffix if less than 2 suffixes exists
}
hint_codes = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'wowRealySecretKey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'home'


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    total_score = db.Column(db.Integer, default=0)
    total_rounds_played = db.Column(db.Integer, default=0)
    total_hints_used_amount = db.Column(db.Integer, default=0, nullable=False)
    volume = db.Column(db.Integer, default=50)  # well I need to save it somehow
    amount_of_guesses = db.Column(db.Integer, default=1)  # chosen with slider before session beginning
    amount_of_rounds = db.Column(db.Integer, default=1)  # chosen with slider before session beginning
    profile_image = db.Column(db.String[16], nullable=False, default='0000000000000000')

    sessions = db.relationship('Sessions', backref='Users')


class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_score = db.Column(db.Integer, default=0)  # total score of a game session
    total_hints = db.Column(db.String(32), default='')  # total numerical amount of hints used in every round
    rounds = db.Column(db.Integer, default=0)
    ended = db.Column(db.Boolean, default=False)

    round = db.relationship('Rounds', backref='Sessions')


class Rounds(db.Model):
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), primary_key=True, nullable=False)

    amount_of_hints_used = db.Column(db.Integer, default=0)  # numerical value of hints used in every round
    hints_available = db.Column(db.String(16),
                                default='')  # sequence of hints generated on the beginning of every round
    hints_used = db.Column(db.String(16), default='')  # hints which were taken from the sequence
    answer = db.Column(db.String(128), default='')  # randomly chosen country name
    current_round = db.Column(db.Integer, default=0)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# --------------------------------------------------------------#

def generate_random_answer():
    answer = country_names_list[random.randint(0, len(country_names_list) - 1)]
    return answer


def generate_hint_sequence():
    hint_code_sequence = ""
    hint_code_sequence_list = hint_codes
    random.shuffle(hint_code_sequence_list)
    for hint_code in hint_code_sequence_list:
        hint_code_sequence += hint_code
    return hint_code_sequence


def get_hint_response(hint_code, info_json):
    try:
        hint_json = info_json[0][possible_hints_list[hint_code]]
        match hint_code:
            case 'a':
                return f"Capital city: {hint_json[0]}"
            case 'b':
                return f"Continent: {hint_json[0]}"
            case 'c':
                if hint_json:
                    return "Landlocked"
                else:
                    return "Isn't Landlocked"
            case 'd':
                return f"Population of {hint_json} people"
            case 'e':
                return f"Area {hint_json} km^2"
            case 'f':
                if hint_json:
                    return "Independent"
                else:
                    return "Isn't Independent"
            case 'g':
                return f"Currency symbol is {hint_json.get(list(hint_json)[0]).get('symbol')}"
            case 'h':
                return hint_json.get("svg")
            case 'i':
                return hint_json.get("svg")
            case 'j':
                return f"Cars drive on the {hint_json.get('side')} side of the road"
            case 'k':
                return f"{hint_json.get('root')} {hint_json.get('suffixes')[0]}"
            case _:
                return 'Invalid hint code'
    except Exception as e:
        print(e)


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if request.form.get('sign-in'):  # for login
            user = Users.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                flash('Login is successful.')
                return redirect('/')
            else:
                flash('Login Unsuccessful. Please check username and password')
                return render_template('home.html')

        else:  # for registration
            profile_image = ''
            for j in range(16):
                if random.randint(0, 1) == 1:
                    profile_image += "1"
                else:
                    profile_image += "0"

            hashed_password = generate_password_hash(password, method='scrypt')

            new_user = Users(username=username, password=hashed_password, profile_image=profile_image)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/home')
    else:
        return render_template('home.html')


@app.route('/', methods=['GET', 'POST'])
@login_required
def start_menu():
    if request.method == 'POST':
        amount_of_guesses = request.form.get('guesses-range')
        amount_of_rounds = request.form.get('rounds-range')
        current_user.amount_of_guesses = int(amount_of_guesses)
        current_user.amount_of_rounds = int(amount_of_rounds)

        hint_code_sequence = generate_hint_sequence()
        hint_code = hint_code_sequence[0]
        hint_code_sequence = hint_code_sequence[1:]

        new_session = Sessions(user_id=current_user.id, rounds=amount_of_rounds)
        db.session.add(new_session)
        db.session.commit()

        new_round = Rounds(
            session_id=Sessions.query.filter_by(user_id=current_user.id).order_by(Sessions.id.desc()).first().id,
            current_round=1, answer=generate_random_answer(), hints_available=hint_code_sequence,
            hints_used=hint_code)
        db.session.add(new_round)

        current_user.total_rounds_played += 1
        db.session.commit()

        return redirect(f'/game/{new_session.id}/round')
    else:
        settings_data = {
            'volume': current_user.volume,
            'amount_of_guesses': current_user.amount_of_guesses,
            'amount_of_rounds': current_user.amount_of_rounds
        }

        latest_session_data = Sessions.query.filter_by(user_id=current_user.id).order_by(Sessions.id.desc()).first()
        username = current_user.username
        user_id = current_user.id
        return render_template('start-menu.html',
                               latest_session_data=latest_session_data,
                               settings_data=settings_data,
                               max_rounds_amount=max_rounds_amount,
                               max_guesses_amount=max_guesses_amount,
                               username=username,
                               user_id=user_id)


@app.route('/game/<int:session_id>/round', methods=['GET', 'POST'])
@login_required
def game(session_id):
    round_data = Rounds.query.filter_by(session_id=session_id).first()
    session_data = Sessions.query.filter_by(id=session_id).first()

    if request.method == 'POST':
        if request.form.get('answer-button'):
            if request.form.get(round_data.answer):
                session_data.total_score += win_score

            round_data.answer = generate_random_answer()

            hint_code_sequence = generate_hint_sequence()

            round_data.hints_used = hint_code_sequence[0]
            round_data.hints_available = hint_code_sequence[1:]

            session_data.total_hints += f'{round_data.amount_of_hints_used} \t'
            round_data.amount_of_hints_used = 0

            if round_data.current_round < current_user.amount_of_rounds:
                round_data.current_round += 1
                current_user.total_rounds_played += 1
                db.session.commit()
                return redirect(f'/game/{session_id}/round')
            else:
                current_user.total_score += Sessions.query.filter_by(user_id=current_user.id).order_by(
                    Sessions.id.desc()).first().total_score
                session_data.ended = True
                db.session.commit()
                return redirect(f'/game/{session_id}')
        else:  # request.form.get('hint-button')
            if round_data.amount_of_hints_used < max_hints:
                current_user.total_hints_used_amount += 1
                round_data.amount_of_hints_used += 1
                session_data.total_score -= hint_price
                round_data.hints_used += round_data.hints_available[0]
                round_data.hints_available = round_data.hints_available[1:]

                db.session.commit()
            return redirect(f'/game/{session_id}/round')
    else:
        try:
            if not session_data.ended:
                info_json = json.loads(requests.get(api_url + f'name/{round_data.answer}').text)

                hints_to_display = []
                for hint_code in round_data.hints_used:
                    hint_string = get_hint_response(hint_code, info_json)
                    if hint_string != NoneType:
                        hints_to_display.append(hint_string)

                settings_data = {
                    'volume': current_user.volume,
                    'amount_of_guesses': current_user.amount_of_guesses,
                    'amount_of_rounds': current_user.amount_of_rounds
                }
                return render_template('game-round.html',
                                       round_data=round_data,
                                       hints_to_display=hints_to_display,
                                       session_data=session_data,
                                       country_names_list=country_names_list,
                                       settings_data=settings_data)
            else:
                return render_template('no-user-exist.html', text_message="Session ended", title="Session ended")
        except Exception as e:
            print(e)
            return render_template('no-user-exist.html', text_message="No such session exists", title="No session")


@app.route('/game/<int:session_id>', methods=['GET'])
@login_required
def session_summary(session_id):
    if Sessions.query.filter_by(id=session_id).first():
        session_data = Sessions.query.filter_by(id=session_id).first()
        username = Users.query.filter_by(id=session_data.user_id).first().username
        return render_template('game-session-summary.html',
                               session_data=session_data,
                               username=username)
    else:
        return render_template('no-user-exist.html', text_message="No such session exists", title="No session")


@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template('no-user-exist.html', text_message="404 Not Found", title="404 Not Found")


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        try:
            current_user.volume = int(request.form.get('volume-range'))
            db.session.commit()
            return redirect(f'/settings')
        except Exception as e:
            print(e)
            return e
    else:
        volume = current_user.volume
        return render_template('settings.html',
                               volume=volume)


@app.route('/scoreboard', methods=['GET'])
@login_required
def scoreboard_page():
    sessions_data = Sessions.query.filter_by(user_id=current_user.id).order_by(Sessions.id).all()
    return render_template('scoreboard.html',
                           sessions_data=sessions_data)


@app.route('/clear-the-scoreboard', methods=['GET', 'POST'])
@login_required
def clear_the_scoreboard():
    user_sessions = Sessions.query.filter_by(user_id=current_user.id).all()
    for session in user_sessions:
        db.session.delete(Rounds.query.filter_by(session_id=session.id).first())
        db.session.delete(session)
    db.session.commit()
    return redirect('/scoreboard')


@app.route('/remove-entry/<int:session_id>')
@login_required
def remove_entry(session_id):
    if Sessions.query.filter_by(id=session_id).first().user_id == current_user.id:
        db.session.delete(Rounds.query.filter_by(session_id=session_id).first())
        db.session.delete(Sessions.query.filter_by(id=session_id).first())
        db.session.commit()
    else:
        flash("You can't remove other player sessions.")
    return redirect('/scoreboard')


@app.route('/top-players', methods=['GET'])
def top_players():
    usernames = []
    total_scores = []
    total_rounds = []
    ids = []

    for user in Users.query.order_by(Users.total_score.desc()).limit(100).all():
        ids.append(user.id)
        usernames.append(user.username)
        if user.total_rounds_played != 0:
            total_scores.append(round(user.total_score / user.total_rounds_played))
        else:
            total_scores.append(0)
        total_rounds.append(user.total_rounds_played)

    return render_template('top-players.html',
                           usernames=usernames,
                           total_scores=total_scores,
                           total_rounds=total_rounds,
                           ids=ids)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect('/home')


@app.route('/user/<int:user_id>')
def user_profile(user_id):
    if request.method == 'POST':
        return redirect(f'/user/{user_id}')
    else:
        try:
            print(Users.query.filter_by(id=user_id).first().profile_image)

            user_info = {
                'id': user_id,
                'username': Users.query.filter_by(id=user_id).first().username,
                'total_score': Users.query.filter_by(id=user_id).first().total_score,
                'total_rounds': Users.query.filter_by(id=user_id).first().total_rounds_played,
                'avg_score': round(Users.query.filter_by(id=user_id).first().total_score / 1 + Users.query.filter_by(
                    id=user_id).first().total_rounds_played, 2),
                'avg_hints_used': round(
                    Users.query.filter_by(id=user_id).first().total_hints_used_amount / 1 + Users.query.filter_by(
                        id=user_id).first().total_rounds_played, 2),
                'profile_code': Users.query.filter_by(id=user_id).first().profile_image
            }
            if AnonymousUserMixin:
                return render_template('profile.html',
                                       user_info=user_info,
                                       current_user_id=0)
            else:
                return render_template('profile.html',
                                       user_info=user_info,
                                       current_user_id=current_user.id)
        except Exception as e:
            print(e)
            return render_template('no-user-exist.html', text_message="User not found", title="User 404")


@app.route('/randomize-my-profile-picture', methods=['GET', 'POST'])
@login_required
def randomize_my_profile_picture():
    profile_image = ''
    for j in range(16):
        if random.randint(0, 1) == 1:
            profile_image += "1"
        else:
            profile_image += "0"
    current_user.profile_image = profile_image
    db.session.commit()
    return redirect(f'/user/{current_user.id}')


# --------------------------------------------------------------#

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
