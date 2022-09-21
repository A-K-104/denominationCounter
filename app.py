import constance
from routes.basicRoutsHandling import basic_routs_handling


def create():
    db = constance.db
    app = constance.app
    app.register_blueprint(basic_routs_handling)

    @app.before_first_request
    def create_tables():
        db.create_all()

    return app


if __name__ == "__main__":
    create().run(debug=True)