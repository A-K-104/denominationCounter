import constance
from routes.basicRoutsHandling import basic_routs_handling

db = constance.db
app = constance.app
sess = constance.sess
app.register_blueprint(basic_routs_handling)


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":
    app.run(port=5000, host="127.0.0.1")
