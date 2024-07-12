from flask import Flask, request

from services.messengers import MessengerFactory
from utils.logging_utils import initialise_logging_config
from utils.structures import MessengerOptions

app = Flask(__name__)

initialise_logging_config()

@app.route("/income", methods=["GET", "POST"])
def income():
    if request.method == "POST":
        try:
            MessengerFactory.get_messenger(MessengerOptions.EMAIL).receive_message(request.form)
        except Exception as e:
            app.logger.error(f"Error receiving message: {str(e)}", exc_info=True)
            return "Error occurred while processing message", 500
        return "ok"


@app.route("/")
def homepage():
    return "Mail Server is Running now..."


app.run(
    host="0.0.0.0",
    port=10234
)
