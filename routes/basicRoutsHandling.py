from flask import Blueprint, render_template, request
from werkzeug.utils import redirect

import constance
from classes.games import Games
from classes.stations import Stations
from classes.teams import Teams

basic_routs_handling = Blueprint('basic_routs_handling', __name__)
db = constance.db


@basic_routs_handling.route('/', methods=['GET', 'POST'])
def baseRoute():
    return redirect("/home")


@basic_routs_handling.route('/home', methods=['GET', 'POST'])
def home():
    if request.args.__contains__("messages"):
        return render_template("home.html", messages=request.args.get("messages"))
    return render_template("home.html")


@basic_routs_handling.route('/teams', methods=['GET', 'POST'])
def teams():
    message = ""
    if request.method == "POST":
        if request.form.__contains__('team_name') and request.form.__contains__('team_color'):
            if db.session.query(Teams.name).filter_by(name=request.form['team_name']).first() is None:
                if db.session.query(Teams.color).filter_by(color=request.form['team_color']).first() is None:
                    new_teams = Teams(name=request.form['team_name'], color=request.form['team_color'])
                    db.session.add(new_teams)
                    db.session.commit()
                else:
                    message = "color already exist"
            else:
                message = "name already exist"
        else:
            message = "failed to get par"
    teams = Teams.query.order_by(Teams.id)
    return render_template("teams.html", teams=list(teams), message=message)


@basic_routs_handling.route('/log_to_game', methods=['GET', 'POST'])
def log_to_game():
    if request.method == "POST":
        game = db.session.query(Games.id).filter_by(id=request.form['game_id']).first()
        if game is None:
            return redirect(f"/home?messages=wrong_error_code")
        return game.name
    return redirect(f"/home?messages=wrong_method")


@basic_routs_handling.route('/games', methods=['GET', 'POST'])
def games():
    message = ""
    if request.method == "POST":
        if request.form.__contains__('game_name'):
            if db.session.query(Teams.name).filter_by(name=request.form['game_name']).first() is None:
                new_game = Games(name=request.form['game_name'])
                db.session.add(new_game)
                db.session.commit()
            else:
                message = "name already exist"
        else:
            message = "failed to get par"
    games = Games.query.order_by(Games.id)
    return render_template("games.html", games=list(games), message=message)


@basic_routs_handling.route('/stations', methods=['GET', 'POST'])
def stations():
    message = ""
    if request.method == "POST":
        if request.form.__contains__('stations_name') and request.form.__contains__('stations_point'):
            if db.session.query(Stations.name).filter_by(name=request.form['stations_name']).first() is None:
                new_stations = Stations(name=request.form['stations_name'], point=request.form['stations_point'])
                db.session.add(new_stations)
                db.session.commit()
            else:
                message = "name already exist"
        else:
            message = "failed to get par"
    stations = Stations.query.order_by(Stations.id)
    return render_template("stations.html", stations=list(stations), message=message)
