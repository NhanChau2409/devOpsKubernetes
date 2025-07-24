from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import time

app = Flask(__name__)

# Database configuration from environment variables
DB_HOST = os.environ.get("DB_HOST", "postgres-service")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "todos_db")
DB_USER = os.environ.get("DB_USER", "todos_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "todos_password_123")

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Todo Model
class Todo(db.Model):
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def init_db():
    """Simple database initialization function"""
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database initialized successfully")
            return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


@app.route("/todos", methods=["GET"])
def get_todos():
    """Get all todos"""
    try:
        todos = Todo.query.order_by(Todo.created_at.desc()).all()
        return jsonify([todo.to_dict() for todo in todos])
    except Exception as e:
        print(f"Error fetching todos: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500


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

        # Create new todo
        new_todo = Todo(text=todo_text, completed=False)
        db.session.add(new_todo)
        db.session.commit()

        return jsonify(new_todo.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error creating todo: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    """Update a todo (mark as completed)"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({"error": "Todo not found"}), 404

        data = request.get_json()
        if "completed" in data:
            todo.completed = data["completed"]
        if "text" in data:
            todo.text = data["text"].strip()

        db.session.commit()
        return jsonify(todo.to_dict())

    except Exception as e:
        db.session.rollback()
        print(f"Error updating todo: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    """Delete a todo"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({"error": "Todo not found"}), 404

        db.session.delete(todo)
        db.session.commit()

        return jsonify({"message": "Todo deleted successfully"})

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting todo: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/health")
def health():
    """Simple health check"""
    return jsonify({"status": "ok"})


@app.route("/")
def root():
    """Root endpoint"""
    return jsonify({"service": "Todo Backend API", "version": "2.0.0"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Todo Backend started on port {port}")

    # Simple database initialization
    init_db()

    app.run(host="0.0.0.0", port=port, debug=False)
