from flask import Blueprint, render_template, request
from werkzeug.utils import redirect
import constance
from classes.database.GameSession import GameSession

from classes.database.Games import Games
from classes.database.stations import Stations
from classes.database.stationsTakeOvers import StationsTakeOvers
from classes.database.teams import Teams

basic_routs_handling = Blueprint('basic_routs_handling', __name__)
db = constance.db


@basic_routs_handling.route('/', methods=['GET', 'POST'])
def baseRoute():
    return redirect("/home")


@basic_routs_handling.route('/home', methods=['GET', 'POST'])
def home():
    game_session_name = None
    method = 'create'
    if request.method == "POST":
        if request.form.__contains__("gameSessionName"):
            if request.form.__contains__('create'):
                if db.session.query(GameSession).filter_by(name=request.form["gameSessionName"]).first() is None:
                    new_game = GameSession(name=request.form["gameSessionName"])
                    db.session.add(new_game)
            elif request.form.__contains__('edit'):
                if db.session.query(GameSession).filter_by(name=request.form["gameSessionName"]).first() is None:
                    game_session_name = GameSession.query.get(request.form["edit"])
                    game_session_name.name = request.form["gameSessionName"]

        elif request.form.__contains__("removeGameId"):
            game = GameSession.query.get(request.form["removeGameId"])
            db.session.delete(game)
        elif request.form.__contains__("disableEnableGame"):
            game = GameSession.query.get(request.form["disableEnableGame"])
            game.active = not game.active
        elif request.form.__contains__("manageGame"):
            game_session_name = GameSession.query.get(request.form["manageGame"])
            method = 'edit'
        db.session.commit()

    games_sessions = GameSession.query.all()
    return render_template("home.html", gamesSessions=games_sessions, method=method, gameSessionName=game_session_name)


@basic_routs_handling.route('/enterPage', methods=['GET', 'POST'])
def game_pome_page():
    if request.args.__contains__("messages"):
        return render_template("enterPage.html", messages=request.args.get("messages"))
    return render_template("enterPage.html")


@basic_routs_handling.route('/games-menu', methods=['GET', 'POST'])
def games_menu():
    if not request.args.__contains__('id') or \
            db.session.query(GameSession).filter_by(id=request.args.get("id")).first() is None:
        return redirect("/")

    return render_template("gameHomePage.html", id=request.args.get("id"))


@basic_routs_handling.route('/teams', methods=['GET', 'POST'])
def teams():
    if not request.args.__contains__('id') or \
            db.session.query(GameSession).filter_by(id=request.args.get("id")).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.args.get("id")).first()
    message = ""
    if request.method == "POST":
        if request.form.__contains__('team_name') and request.form.__contains__('team_color'):
            if db.session.query(Teams). \
                    filter_by(name=request.form['team_name'], session=request.args.get("id")).first() is None:
                if db.session.query(Teams). \
                        filter_by(color=request.form['team_color'], session=request.args.get("id")).first() is None:
                    new_teams = Teams(name=request.form['team_name'], color=request.form['team_color'])
                    game_session.teams.append(new_teams)
                    db.session.commit()
                else:
                    message = "color already exist"
            else:
                message = "name already exist"
        elif request.form.__contains__('removeTeamId'):
            team = Teams.query.get(request.form['removeTeamId'])
            if team is not None:
                db.session.delete(team)
                db.session.commit()
        else:
            message = "failed to get par"
    session_teams = db.session.query(Teams).filter_by(session=request.args.get("id")).all()
    return render_template("teams.html", teams=list(session_teams), message=message, id=request.args.get("id"))


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


@basic_routs_handling.route('/old-games', methods=['GET', 'POST'])
def old_games():
    if not request.args.__contains__('id') or \
            db.session.query(GameSession).filter_by(id=request.args.get("id")).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.args.get("id")).first()
    # todo: calc game score.
    return render_template("games.html", games=list(game_session.games))


@basic_routs_handling.route('/stations', methods=['GET', 'POST'])
def stations():
    if not request.args.__contains__('id') or \
            db.session.query(GameSession).filter_by(id=request.args.get("id")).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.args.get("id")).first()
    message = ""
    if request.method == "POST":
        if request.form.__contains__('stations_name') and request.form.__contains__('stations_point'):
            if db.session.query(Stations).filter_by(name=request.form['stations_name'],
                                                    session=request.args.get("id")).first() is None:
                new_stations = Stations(name=request.form['stations_name'], point=request.form['stations_point'])
                game_session.stations.append(new_stations)
                db.session.commit()
            else:
                message = "name already exist"
        elif request.form.__contains__('removeStationId'):
            station = Stations.query.get(request.form['removeStationId'])
            if station is not None:
                db.session.delete(station)
                db.session.commit()
        else:
            message = "failed to get par"
    session_station = db.session.query(Stations).filter_by(session=request.args.get("id")).all()
    return render_template("stations.html", stations=list(session_station), message=message, id=request.args.get("id"))


@basic_routs_handling.route('/live-game', methods=['GET', 'POST'])
def live_game():
    #   todo: added error message
    message = ""
    if not request.args.__contains__("session-id") or \
            db.session.query(GameSession).filter_by(id=request.args["session-id"]).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.args["session-id"]).first()
    if multi_games_running(game_session.games) != -1:
        return render_template("live_game.html", stations=list(game_session.stations), message=message,
                               gameId=request.args['session-id'])
    return redirect("/")


@basic_routs_handling.route('/live-station', methods=['GET', 'POST'])
def live_station():
    print()
    if not request.args.__contains__("session-id") or \
            db.session.query(GameSession).filter_by(id=request.args["session-id"]).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.args["session-id"]).first()
    game_id = multi_games_running(game_session.games)
    if game_id != -1:

        if request.method == "POST":
            game = db.session.query(Games).filter_by(id=game_id).first()
            game.stationsTakeOvers.append(
                StationsTakeOvers(stationId=request.args['station-id'], teamId=request.form["setStatus"]))
            db.session.commit()

        return render_template("live_station.html", teams=list(game_session.teams),
                               sessionId=request.args['session-id'],
                               stationId=request.args['station-id'],
                               teamInControl=int(team_in_control(game_id)))
    return redirect("/")


@basic_routs_handling.route('/new-game', methods=['GET', 'POST'])
def games1():
    if not request.args.__contains__('id') or \
            db.session.query(GameSession).filter_by(id=request.args.get("id")).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.args.get("id")).first()
    for game in game_session.games:
        game.active = False
    game_session.games.append(Games(active=True))
    db.session.commit()
    return redirect(f"/run-game?id={game_session.id}")


@basic_routs_handling.route('/run-game', methods=['GET', 'POST'])
def games2():
    if not request.args.__contains__('id') or \
            db.session.query(GameSession).filter_by(id=request.args.get("id")).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.args.get("id")).first()
    if multi_games_running(game_session.games) == -1:
        return "bad"
    return "good"


@basic_routs_handling.route('/enter-to-session', methods=['GET', 'POST'])
def enter_to_session():
    print("asdf")
    if not request.form.__contains__('gameSessionId') or \
            db.session.query(GameSession).filter_by(id=request.form["gameSessionId"]).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.form["gameSessionId"]).first()
    if multi_games_running(game_session.games) != -1:
        return redirect(f"/live-game?session-id={game_session.id}")


def multi_games_running(games: list) -> int:
    running_game: int = -1
    for game in games:
        if game.active:
            if running_game != -1:
                return -1
            running_game = game.id
    return running_game


def team_in_control(game: int):
    print()
    return db.session.query(StationsTakeOvers).filter_by(game=game)\
        .order_by(StationsTakeOvers.date_created.desc()).first().teamId

# @basic_routs_handling.route('/game-is-alive', methods=['GET'])
# def game_is_alive() -> tuple[str, int]:
#     if db.session.query(Games).filter_by(id=request.args.get('game-id')).first() is not None:
#         game = Games.query.get(request.args['game-id'])
#         print(game.active)
#
#         if game.active:
#             return "true", 200
#     return "false", 201
