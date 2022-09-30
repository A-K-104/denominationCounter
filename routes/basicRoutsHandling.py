import constance
from datetime import datetime
from flask import Blueprint, render_template, request
from werkzeug.utils import redirect

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
def teams_handler():
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
    # todo: calc game show all games score

    return str(calc_game(game_session, game_session.games[-1]))
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
    if multi_games_running(game_session.games) is not None:
        return render_template("live_game.html", stations=list(game_session.stations), message=message,
                               gameId=request.args['session-id'])
    return redirect("/")


@basic_routs_handling.route('/live-station', methods=['GET', 'POST'])
def live_station():
    if not request.args.__contains__("session-id") or \
            db.session.query(GameSession).filter_by(id=request.args["session-id"]).first() is None:
        return redirect("/")

    if not request.args.__contains__("station-id") or \
            db.session.query(Stations).filter_by(id=request.args["station-id"],
                                                 session=request.args["session-id"]).first() is None:
        return redirect("/")

    game_session = db.session.query(GameSession).filter_by(id=request.args["session-id"]).first()
    game_id = multi_games_running(game_session.games)
    if game_id is not None:

        if request.method == "POST":
            game = db.session.query(Games).filter_by(id=game_id.id).first()
            game.stationsTakeOvers.append(
                StationsTakeOvers(stationId=request.args['station-id'], teamId=request.form["setStatus"]))
            db.session.commit()

        return render_template("live_station.html", teams=list(game_session.teams),
                               sessionId=request.args['session-id'],
                               stationId=request.args['station-id'],
                               teamInControl=int(team_in_control(game_id.id, int(request.args['station-id']))))
    return redirect("/")


@basic_routs_handling.route('/new-game', methods=['GET', 'POST'])
def new_game():
    if not request.args.__contains__('id') or \
            db.session.query(GameSession).filter_by(id=request.args.get("id")).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.args.get("id")).first()
    for game in game_session.games:
        if game.active:
            game.date_ended = datetime.utcnow()
            game.active = False
    game_session.games.append(Games(active=True))
    db.session.commit()
    return redirect(f"/run-game?id={game_session.id}")


@basic_routs_handling.route('/run-game', methods=['GET', 'POST'])
def running_game_manage():
    if not request.args.__contains__('id') or \
            db.session.query(GameSession).filter_by(id=request.args.get("id")).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.args.get("id")).first()
    running_game = multi_games_running(game_session.games)
    if running_game is None:
        return "error multiply games are running or none"
    if request.method == "POST":
        running_game.date_ended = datetime.utcnow()
        running_game.active = False
    return render_template("manageRunningGame.html")


@basic_routs_handling.route('/run-game/stop', methods=['GET', 'POST'])
def running_game_stop():
    if not request.args.__contains__('id') or \
            db.session.query(GameSession).filter_by(id=request.args.get("id")).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.args.get("id")).first()
    running_game = multi_games_running(game_session.games)
    if running_game is None:
        return "error multiply games are running or none"
    running_game.date_ended = datetime.utcnow()
    running_game.active = False
    db.session.commit()
    return redirect(f"/games-menu?id={game_session.id}")


@basic_routs_handling.route('/run-game/get-score', methods=['GET', 'POST'])
def running_game_get_live():
    if not request.args.__contains__('id') or \
            db.session.query(GameSession).filter_by(id=request.args.get("id")).first() is None:
        return {"status": 400, "error": "faild to find session"}, 400
    game_session = db.session.query(GameSession).filter_by(id=request.args.get("id")).first()

    return calc_game(game_session, game_session.games[-1])


@basic_routs_handling.route('/enter-to-session', methods=['GET', 'POST'])
def enter_to_session():
    print("asdf")
    if not request.form.__contains__('gameSessionId') or \
            db.session.query(GameSession).filter_by(id=request.form["gameSessionId"]).first() is None:
        return redirect("/")
    game_session = db.session.query(GameSession).filter_by(id=request.form["gameSessionId"]).first()
    if multi_games_running(game_session.games) is not None:
        return redirect(f"/live-game?session-id={game_session.id}")
    return redirect("/")


@basic_routs_handling.route('/game-is-alive', methods=['GET'])
def game_is_alive() -> (str, int):

    if not request.args.__contains__("session-id") or \
            db.session.query(GameSession).filter_by(id=request.args["session-id"]).first() is None:
        return "false", 400

    if not request.args.__contains__("station-id") or \
            db.session.query(Stations).filter_by(id=request.args["station-id"],
                                                 session=request.args["session-id"]).first() is None:
        return "false", 400

    game_session = db.session.query(GameSession).filter_by(id=request.args["session-id"]).first()

    if len(game_session.games) > 0 and game_session.games[-1].date_ended is None:
        return "true", 200
    return "false", 202


def multi_games_running(games: list) -> None or Games:
    running_game: Games = None
    for game in games:
        if game.active:
            if running_game is not None:
                return None
            running_game = game
    return running_game


def team_in_control(game: int, station_id:int):
    team_in = db.session.query(StationsTakeOvers).filter_by(game=game, stationId=station_id) \
        .order_by(StationsTakeOvers.date_created.desc()).first()
    if team_in is not None:
        return team_in.teamId
    return -1


def calc_game(game_session: GameSession, game: Games) -> None or dict:
    if not game_session.games.__contains__(game):
        return None
    result: dict = {}
    for team in game_session.teams:
        result[team.id] = 0

    game_ended = game.date_ended
    if game_ended is None:
        game_ended = datetime.utcnow()

    for station in game_session.stations:
        sub_result = station_calc(game_session.teams, station,
                                  game.stationsTakeOvers, game.date_created, game_ended)
        for team in game_session.teams:
            result[team.id] += sub_result[team.id]
    return result


def get_list_of_take_overs_per_station(station: Stations, take_overs: list) -> list:
    new_take_over: list = []
    for take_over in take_overs:
        if take_over.stationId == station.id:
            new_take_over.append(take_over)
    return new_take_over


def station_calc(teams: list, station: Stations,
                 take_overs: list, last_take_over: datetime,
                 game_ended: datetime) -> None or dict:
    result: dict = {}

    for team in teams:
        result[team.id] = 0
    take_overs = get_list_of_take_overs_per_station(station, take_overs)
    if len(take_overs) > 0:
        for take_over in take_overs:
            if result.__contains__(take_over.teamId):
                result[take_over.teamId] += (take_over.date_created - last_take_over).seconds / 60 * station.point
                last_take_over = take_over.date_created
        result[take_overs[-1].teamId] += (game_ended - last_take_over).seconds / 60 * station.point
    return result


