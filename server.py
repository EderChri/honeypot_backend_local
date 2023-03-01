from flask import Flask, request

import mailgun

app = Flask(__name__)   

print(__name__)


@app.route("/income", methods=["GET", "POST"])
def income():
    if request.method == "POST":
        mailgun.on_receive(request.form)
        print("YESYEYSYEYSYEYSYEYSYEY")
    return "ok"


@app.route("/")
def homepage():
    return "Mail Server is Running now..."


app.run(
    host="0.0.0.0",
    port=10234
)