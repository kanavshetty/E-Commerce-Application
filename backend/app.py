from flask import Flask, render_template
from api.DatabaseConnection.connection import DBConnection

app = Flask(__name__)

@app.route("/")
def home():
    return("Online Store Backend is Running!!")

if __name__ == "__main__":
    DBConnection.get_instance().connect()
    app.run(debug=True)