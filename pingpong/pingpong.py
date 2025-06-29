from flask import Flask

app = Flask(__name__)
counter = 0


@app.route("/pingpong", methods=["GET"])
def pingpong():
    global counter
    response = f"pong {counter}"
    counter += 1
    return response, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
