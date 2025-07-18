from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# Data storage file
TODOS_FILE = "/data/todos.json"


def load_todos():
    """Load todos from JSON file"""
    try:
        if os.path.exists(TODOS_FILE):
            with open(TODOS_FILE, "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading todos: {e}")
        return []


def save_todos(todos):
    """Save todos to JSON file"""
    try:
        os.makedirs(os.path.dirname(TODOS_FILE), exist_ok=True)
        with open(TODOS_FILE, "w") as f:
            json.dump(todos, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving todos: {e}")
        return False


@app.route("/todos", methods=["GET"])
def get_todos():
    """Get all todos"""
    todos = load_todos()
    return jsonify(todos)


@app.route("/todos", methods=["POST"])
def create_todo():
    """Create a new todo"""
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "Todo text is required"}), 400

        todo_text = data["text"].strip()
        if not todo_text:
            return jsonify({"error": "Todo text cannot be empty"}), 400

        # Load existing todos
        todos = load_todos()

        # Create new todo
        new_todo = {
            "id": len(todos) + 1,
            "text": todo_text,
            "completed": False,
            "created_at": datetime.now().isoformat(),
        }

        # Add to list
        todos.append(new_todo)

        # Save to file
        if save_todos(todos):
            return jsonify(new_todo), 201
        else:
            return jsonify({"error": "Failed to save todo"}), 500

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    """Update a todo (mark as completed)"""
    try:
        todos = load_todos()

        # Find the todo
        todo = next((t for t in todos if t["id"] == todo_id), None)
        if not todo:
            return jsonify({"error": "Todo not found"}), 404

        data = request.get_json()
        if "completed" in data:
            todo["completed"] = data["completed"]

        if save_todos(todos):
            return jsonify(todo)
        else:
            return jsonify({"error": "Failed to update todo"}), 500

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    """Delete a todo"""
    try:
        todos = load_todos()

        # Find and remove the todo
        todo = next((t for t in todos if t["id"] == todo_id), None)
        if not todo:
            return jsonify({"error": "Todo not found"}), 404

        todos = [t for t in todos if t["id"] != todo_id]

        if save_todos(todos):
            return jsonify({"message": "Todo deleted successfully"})
        else:
            return jsonify({"error": "Failed to delete todo"}), 500

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "todo-backend"})


@app.route("/")
def root():
    """Root endpoint with API information"""
    return jsonify(
        {
            "service": "Todo Backend API",
            "version": "1.0.0",
            "endpoints": {
                "GET /todos": "Get all todos",
                "POST /todos": "Create a new todo",
                "PUT /todos/<id>": "Update a todo",
                "DELETE /todos/<id>": "Delete a todo",
                "GET /health": "Health check",
            },
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Todo Backend started on port {port}")
    print(f"Todos will be stored in: {TODOS_FILE}")
    app.run(host="0.0.0.0", port=port, debug=False)
