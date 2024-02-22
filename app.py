from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder="build", static_url_path="/")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://eidetic:eideticpass@localhost/eidetic"
)

CORS(app)

db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)


class Note(db.Model):
    note_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    hash = db.Column(db.String(64), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@app.route("/get-notes", methods=["GET"])
def get_notes():
    notes = Note.query.filter_by(user_id=request.args.get("user_id"))

    return jsonify([{"content": n.content} for n in notes])


@app.route("/add-note", methods=["POST"])
def add_note():
    new_note = Note(
        title="",
        user_id=1,
        content=request.json["content"],
        hash="",
    )

    try:
        db.session.add(new_note)
        db.session.commit()
    except Exception as e:
        message = f"An exception occurred while committing: {str(e)}"
        print(message)

        return (
            jsonify(
                {
                    "message": message,
                }
            ),
            400,
        )

    return (
        jsonify(
            {
                "message": "Successfully created note",
            }
        ),
        201,
    )


@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(use_reloader=True, port=5000, threaded=True)
