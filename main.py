import constance
from routes.basicRoutsHandling import basic_routs_handling

db = constance.db
app = constance.app
sess = constance.sess
app.register_blueprint(basic_routs_handling)


@app.before_first_request
def create_tables():
    db.create_all()

#
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
