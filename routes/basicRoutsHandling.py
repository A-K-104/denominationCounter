import datetime

from flask import Blueprint, render_template, request
from werkzeug.utils import redirect
import __init__
# import constance
from classes.games import Games
from classes.stations import Stations
from classes.teams import Teams

basic_routs_handling = Blueprint('basic_routs_handling', __name__)
db = __init__.db


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
        game = Games.query.get(request.form["game_id"])
        if game is None:
            return redirect(f"/home?messages=wrong_error_code")
        if game.active:
            return redirect(f"/live-game?game-id={game.id}")
        else:
            return redirect(f"/home?messages=game_{game.id}_is_not_active")
    return redirect(f"/home?messages=wrong_method")


@basic_routs_handling.route('/games', methods=['GET', 'POST'])
def games():
    message = ""
    if request.method == "POST":
        if request.form.__contains__('game_name'):
            if db.session.query(Games.name).filter_by(name=request.form['game_name']).first() is None:
                new_game = Games(name=request.form['game_name'])
                db.session.add(new_game)
                db.session.commit()
            else:
                message = "name already exist"
        elif request.form.__contains__('setStatus') and request.form.__contains__('gameId'):
            games = Games.query.order_by(Games.id)
            stations = Stations.query.order_by(Stations.id)
            for game in games:
                if game.active:
                    for station in stations:
                        arr_of_game: dict = game.points
                        arr_of_game = setPoints(arr_of_game,station)
                        game.points = None
                        db.session.commit()

                        game.points = arr_of_game
                        station.team = -1
                        station.take_over_time = datetime.datetime.utcnow()
                game.active = (str(game.id) == request.form['gameId'])

            db.session.commit()

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


@basic_routs_handling.route('/live-game', methods=['GET', 'POST'])
def live_game():
    message = ""
    if not request.args.__contains__("game-id"):
        return redirect("/home?messages=missing_game_id")
    if request.method == "POST":
        if request.form.__contains__('station-id'):
            return redirect(
                f"/station-handler?station-id={request.form['station-id']}&game-id={request.args.get('game-id')}")
    stations = Stations.query.order_by(Stations.id)
    return render_template("live_game.html", stations=list(stations), message=message,
                           gameId=request.args.get('game-id'))


def setPoints(arr_of_game, station):
    if arr_of_game is not None:
        if arr_of_game.get(str(station.team)) is None:
            arr_of_game.update({str(station.team): {str(station.id): 0}})
    else:
        arr_of_game = {str(station.team): {str(station.id): 0}}
    added_points = (datetime.datetime.utcnow() - station.take_over_time).seconds * station.point / 60
    if arr_of_game.get(str(station.team)).get(str(station.id)) is None:
        updatedVal = added_points
    else:
        updatedVal = arr_of_game.get(str(station.team)).get(str(station.id)) + added_points
    station.take_over_time = datetime.datetime.utcnow()
    arr_of_game.update({str(station.team): {str(station.id): updatedVal}})
    return arr_of_game


@basic_routs_handling.route('/station-handler', methods=['GET', 'POST'])
def station_handler():
    message = ""

    if not request.args.__contains__("game-id"):
        return redirect("/home?messages=missing_game_id")
    if not request.args.__contains__("station-id"):
        return redirect("/home?messages=missing_game_id")
    station = Stations.query.get(request.args['station-id'])
    game = Games.query.get(request.args['game-id'])

    if request.method == "POST":
        if request.form.__contains__('teamId'):
            if db.session.query(Teams.id).filter_by(id=request.form['teamId']).first() is None:
                return redirect("/home?messages=failed_to_find_team")
            if not station.team == -1:
                arr_of_game: dict = game.points
                arr_of_game = setPoints(arr_of_game,station)
                game.points = None
                db.session.commit()

                game.points = arr_of_game
                db.session.commit()

            station.team = request.form['teamId']
            db.session.commit()
    teams = Teams.query.order_by(Teams.id)
    return render_template("live_station.html", teams=list(teams), message=message, #F2$4592d
                           teamInControl=station.team,
                           gameId=request.args.get('game-id'),
                           stationId=request.args.get('station-id'))


# @basic_routs_handling.route('/game-is-alive', methods=['GET'])
# def game_is_alive() -> tuple[str, int]:
#     if db.session.query(Games.id).filter_by(id=request.args.get('game-id')).first() is not None:
#         game = Games.query.get(request.args['game-id'])
#         print(game.active)
#
#         if game.active:
#             return "true", 200
#     return "false", 201
