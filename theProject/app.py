from flask import Flask, send_file, render_template_string
import os
import time
import requests

app = Flask(__name__)

IMAGE_PATH = "/data/image.jpg"
TIMESTAMP_PATH = "/data/timestamp.txt"
CACHE_DURATION = 600  # 10 minutes in seconds


@app.route("/")
def home():
    # Ensure /data exists
    os.makedirs("/data", exist_ok=True)
    now = time.time()
    last_fetch = 0
    served_old = False
    # Read last fetch time
    if os.path.exists(TIMESTAMP_PATH):
        with open(TIMESTAMP_PATH, "r") as f:
            try:
                last_fetch = float(f.read().strip())
            except Exception:
                last_fetch = 0
    # Check if image needs to be refreshed
    if not os.path.exists(IMAGE_PATH) or now - last_fetch > CACHE_DURATION:
        # If image is old, serve it once more, then fetch new on next request
        if os.path.exists(IMAGE_PATH) and not served_old:
            served_old = True
        else:
            # Fetch new image
            resp = requests.get("https://picsum.photos/1200", timeout=10)
            if resp.status_code == 200:
                with open(IMAGE_PATH, "wb") as imgf:
                    imgf.write(resp.content)
                with open(TIMESTAMP_PATH, "w") as tf:
                    tf.write(str(now))
                served_old = False
    # Serve the image in HTML
    html = """
    <html>
    <head><title>Random Image</title></head>
    <body>
        <h1>Random Image (cached for 10 minutes)</h1>
        <img src="/image" style="max-width:100%;height:auto;" />
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/image")
def image():
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype="image/jpeg")
    else:
        return "No image cached yet.", 404


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    # Get port from environment variable, default to 8080
    port = int(os.environ.get("PORT", 8080))
    print(f"Server started in port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
