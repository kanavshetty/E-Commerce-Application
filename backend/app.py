from flask import Flask, render_template


app = Flask(__name__)

@app.route("/")
def home():
    return("Online Store Backend is Running!")

if __name__ == "__main__":
    app.run(debug=True)