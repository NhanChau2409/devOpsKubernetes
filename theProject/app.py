from flask import Flask
import os

app = Flask(__name__)


@app.route("/")
def home():
    return "Todo App - Server is running!"


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    # Get port from environment variable, default to 8080
    port = int(os.environ.get("PORT", 8080))
    print(f"Server started in port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
