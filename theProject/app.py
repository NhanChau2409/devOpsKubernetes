from flask import Flask, send_file, render_template_string, request, jsonify
import os
import time
import requests

app = Flask(__name__)

# Configuration from environment variables
IMAGE_PATH = os.environ.get("IMAGE_PATH", "/data/image.jpg")
TIMESTAMP_PATH = os.environ.get("TIMESTAMP_PATH", "/data/timestamp.txt")
CACHE_DURATION = int(os.environ.get("CACHE_DURATION", "600"))  # 10 minutes in seconds
IMAGE_SERVICE_URL = os.environ.get("IMAGE_SERVICE_URL", "https://picsum.photos/1200")
BACKEND_TIMEOUT = int(os.environ.get("BACKEND_TIMEOUT", "5"))
IMAGE_TIMEOUT = int(os.environ.get("IMAGE_TIMEOUT", "10"))
MAX_TODO_LENGTH = int(os.environ.get("MAX_TODO_LENGTH", "140"))

# Backend service configuration
TODO_BACKEND_URL = os.environ.get("TODO_BACKEND_URL", "http://todo-backend:8080")


def fetch_todos_from_backend():
    """Fetch todos from the backend service"""
    try:
        response = requests.get(f"{TODO_BACKEND_URL}/todos", timeout=BACKEND_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch todos: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching todos: {e}")
        return []


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
            resp = requests.get(IMAGE_SERVICE_URL, timeout=IMAGE_TIMEOUT)
            if resp.status_code == 200:
                with open(IMAGE_PATH, "wb") as imgf:
                    imgf.write(resp.content)
                with open(TIMESTAMP_PATH, "w") as tf:
                    tf.write(str(now))
                served_old = False

    # Fetch todos from backend service
    todos = fetch_todos_from_backend()

    # Serve the image and todo app in HTML
    html = """
    <html>
    <head>
        <title>Random Image & Todo App</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .todo-form { margin: 20px 0; }
            .todo-input { padding: 8px; width: 300px; margin-right: 10px; }
            .todo-button { padding: 8px 16px; background: #007bff; color: white; border: none; cursor: pointer; }
            .todo-button:hover { background: #0056b3; }
            .todo-list { list-style: none; padding: 0; }
            .todo-item { padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 4px; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>Random Image (cached for 10 minutes)</h1>
        <img src="/image" style="max-width:100%;height:auto;" />
        <hr/>
        <h2>Todo App</h2>
        <div class="todo-form">
            <input type="text" id="todo-input" class="todo-input" maxlength="{{ max_todo_length }}" placeholder="Enter your todo (max {{ max_todo_length }} chars)" />
            <button onclick="addTodo()" class="todo-button">Add Todo</button>
            <button onclick="testBackend()" style="margin-left: 10px; padding: 8px 16px; background: #28a745; color: white; border: none; cursor: pointer;">Test Backend</button>
        </div>
        <div id="message"></div>
        <ul id="todo-list" class="todo-list">
            {% for todo in todos %}
                <li class="todo-item">{{ todo.text if todo.text else todo }}</li>
            {% endfor %}
        </ul>
        
        <script>
            function addTodo() {
                const input = document.getElementById('todo-input');
                const messageDiv = document.getElementById('message');
                const button = document.querySelector('.todo-button');
                const todoText = input.value.trim();
                
                if (!todoText) {
                    messageDiv.innerHTML = '<p class="error">Please enter a todo item</p>';
                    return;
                }
                
                // Disable button and show loading
                button.disabled = true;
                button.textContent = 'Adding...';
                messageDiv.innerHTML = '<p>Adding todo...</p>';
                
                fetch('/api/todos', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: todoText })
                })
                .then(response => {
                    console.log('Response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('Response data:', data);
                    if (data.success) {
                        messageDiv.innerHTML = '<p class="success">Todo added successfully!</p>';
                        input.value = '';
                        // Refresh the page to show the new todo
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    } else {
                        messageDiv.innerHTML = '<p class="error">Failed to add todo: ' + (data.error || 'Unknown error') + '</p>';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    messageDiv.innerHTML = '<p class="error">Error adding todo: ' + error.message + '</p>';
                })
                .finally(() => {
                    // Re-enable button
                    button.disabled = false;
                    button.textContent = 'Add Todo';
                });
            }
            
            // Allow Enter key to submit
            document.addEventListener('DOMContentLoaded', function() {
                const input = document.getElementById('todo-input');
                if (input) {
                    input.addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') {
                            addTodo();
                        }
                    });
                }
            });
            
            function testBackend() {
                const messageDiv = document.getElementById('message');
                messageDiv.innerHTML = '<p>Testing backend connection...</p>';
                
                fetch('/api/test-backend')
                .then(response => response.json())
                .then(data => {
                    console.log('Backend test result:', data);
                    if (data.success) {
                        messageDiv.innerHTML = '<p class="success">Backend connected successfully!</p>';
                    } else {
                        messageDiv.innerHTML = '<p class="error">Backend connection failed: ' + (data.error || data.backend_response) + '</p>';
                    }
                })
                .catch(error => {
                    console.error('Backend test error:', error);
                    messageDiv.innerHTML = '<p class="error">Error testing backend: ' + error.message + '</p>';
                });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, todos=todos, max_todo_length=MAX_TODO_LENGTH)


@app.route("/api/todos", methods=["POST"])
def create_todo():
    """Create a new todo via the backend service"""
    try:
        data = request.get_json()
        todo_text = data.get("text", "").strip()

        if not todo_text:
            return jsonify({"success": False, "error": "Todo text is required"}), 400

        # Send todo to backend service
        response = requests.post(
            f"{TODO_BACKEND_URL}/todos",
            json={"text": todo_text},
            headers={"Content-Type": "application/json"},
            timeout=BACKEND_TIMEOUT,
        )

        if response.status_code in [200, 201]:
            return jsonify({"success": True, "todo": response.json()})
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Backend returned {response.status_code}",
                    }
                ),
                500,
            )

    except requests.exceptions.RequestException as e:
        return (
            jsonify({"success": False, "error": f"Backend service error: {str(e)}"}),
            500,
        )
    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500


@app.route("/image")
def image():
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype="image/jpeg")
    else:
        return "No image cached yet.", 404


@app.route("/health")
def health():
    return "OK", 200


@app.route("/api/test-backend")
def test_backend():
    """Test connection to backend service"""
    try:
        response = requests.get(f"{TODO_BACKEND_URL}/health", timeout=BACKEND_TIMEOUT)
        if response.status_code == 200:
            return jsonify(
                {
                    "success": True,
                    "backend_status": "connected",
                    "backend_response": response.json(),
                }
            )
        else:
            return jsonify(
                {
                    "success": False,
                    "backend_status": "error",
                    "backend_response": f"Status code: {response.status_code}",
                }
            )
    except requests.exceptions.RequestException as e:
        return jsonify(
            {
                "success": False,
                "backend_status": "disconnected",
                "error": str(e),
                "backend_url": TODO_BACKEND_URL,
            }
        )


if __name__ == "__main__":
    # Get port from environment variable, default to 8080
    port = int(os.environ.get("PORT", 8080))
    print(f"Server started in port {port}")
    print(f"Todo backend URL: {TODO_BACKEND_URL}")
    app.run(host="0.0.0.0", port=port, debug=False)
