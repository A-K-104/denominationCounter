import constance
from routes.basicRoutsHandling import basic_routs_handling


def creat():
    db = constance.db
    app = constance.app
    app.register_blueprint(basic_routs_handling)

    @app.before_first_request
    def create_tables():
        db.create_all()

    return app
#
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
