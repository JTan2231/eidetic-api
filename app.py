import json
import os
import threading
from datetime import datetime

import numpy as np
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
from sklearn.manifold import TSNE

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def create_app():
    app = Flask(__name__, static_folder="build", static_url_path="/")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://eidetic:eideticpass@localhost/eidetic"
    )

    CORS(app)

    db = SQLAlchemy(app)

    # TODO: Change this when auth is implemented
    TEST_ID = 1

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
        # creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    class NoteEdge(db.Model):
        edge_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        note_id_a = db.Column(db.Integer, db.ForeignKey("note.note_id"), nullable=False)
        note_id_b = db.Column(db.Integer, db.ForeignKey("note.note_id"), nullable=False)

    class Embedding(db.Model):
        embedding_id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
        note_id = db.Column(db.Integer, db.ForeignKey("note.note_id"), nullable=False)
        data = db.Column(db.BLOB)
        tsne_x = db.Column(db.Numeric(10, 6), nullable=False)
        tsne_y = db.Column(db.Numeric(10, 6), nullable=False)

    def update_tsne_positions():
        with app.app_context():
            print("updating tsne positions")
            embeddings = Embedding.query.filter_by(user_id=TEST_ID).all()

            if len(embeddings) < 3:
                return

            embed_matrix = np.vstack(
                [np.frombuffer(e.data, dtype=np.float64) for e in embeddings]
            )

            tsne = TSNE(n_components=2, perplexity=min(len(embeddings) - 1, 25))
            projection = tsne.fit_transform(embed_matrix)

            # transforming the projection to range [10, 90] in units of vw/vh
            range_min = -1000
            range_max = 1000
            proj_min = projection.min(axis=0)
            projection = (
                (projection - proj_min) / (projection.max(axis=0) - proj_min)
            ) * (range_max - range_min) + range_min

            for i, embedding in enumerate(embeddings):
                embedding.tsne_x = projection[i, 0]
                embedding.tsne_y = projection[i, 1]

            try:
                db.session.commit()
                print(f"updated {len(embeddings)} positions")
            except Exception as e:
                db.session.rollback()
                print(
                    f"An error occurred processing embedding ids {[em.id for em in embeddings]}: {e}"
                )

    @app.route("/get-notes", methods=["GET"])
    def get_notes():
        notes_embeddings = (
            Note.query.with_entities(
                Note.content, Embedding.tsne_x, Embedding.tsne_y, Note.note_id
            )
            .join(Embedding, Note.note_id == Embedding.note_id)
            .filter(Note.user_id == TEST_ID)
            .all()
        )

        edges = NoteEdge.query.filter(
            NoteEdge.note_id_a.in_([ne[3] for ne in notes_embeddings])
        ).all()

        edge_map = {}
        for e in edges:
            if e.note_id_a in edge_map:
                edge_map[e.note_id_a].append(e.note_id_b)
            else:
                edge_map[e.note_id_a] = [e.note_id_b]

        return jsonify(
            {
                "nodes": [
                    {
                        "id": ne[3],
                        "content": ne[0],
                        "position": [float(ne[1]), float(ne[2])],
                    }
                    for ne in notes_embeddings
                ],
                "edges": [[k, v] for k, v in edge_map.items()],
            }
        )

    def get_openai_embedding(content):
        embedding = None
        try:
            response = client.embeddings.create(
                input=content, model="text-embedding-3-small"
            )

            embedding = response.data[0].embedding

        except Exception as e:
            print(f"Error occurred while using the OpenAI API: {e}")

        return embedding

    @app.route("/top-k-similar", methods=["POST"])
    def top_k_similar():
        k = request.json["count"]
        input_embedding = get_openai_embedding(request.json["content"])
        embeddings = Embedding.query.filter_by(user_id=TEST_ID).all()

        embed_matrix = np.vstack(
            [np.frombuffer(e.data, dtype=np.float64) for e in embeddings]
        )

        scores = []
        for i in range(embed_matrix.shape[0]):
            scores.append((np.dot(input_embedding, embed_matrix[i]), i))

        ids = [s[1] for s in sorted(scores, key=lambda x: x[0])]
        ids = ids[:k]

        return [embeddings[i].note_id for i in ids]

    @app.route("/embedding-threshold-search", methods=["POST"])
    def embedding_threshold_search():
        threshold = 0.05
        input_embedding = get_openai_embedding(request.json["content"])
        embeddings = Embedding.query.filter_by(user_id=TEST_ID).all()

        embed_matrix = np.vstack(
            [np.frombuffer(e.data, dtype=np.float64) for e in embeddings]
        )

        scores = []
        for i in range(embed_matrix.shape[0]):
            scores.append((np.dot(input_embedding, embed_matrix[i]), i))

        print([s[0] for s in scores])
        ids = [s[1] for s in sorted(scores, key=lambda x: x[0]) if s[0] < threshold]

        return [embeddings[i].note_id for i in ids]

    @app.route("/import-channel", methods=["POST"])
    def import_channel():
        url = "http://api.are.na/v2/channels/" + request.json["channel"] + "?per=100"
        channel = json.loads(requests.get(url).content)

        if channel.get("code", None) is not None and channel["code"] >= 400:
            return jsonify({"errors": "invalid channel url"}, status=channel["code"])

        for c in channel["contents"]:
            if c["class"] == "Text":
                new_note = Note(
                    title="", user_id=TEST_ID, content=c["content"], hash=""
                )
                embedding = get_openai_embedding(c["content"])
                db.session.add(new_note)
                db.session.flush()
                if embedding is not None:
                    new_embedding = Embedding(
                        user_id=TEST_ID,
                        note_id=new_note.note_id,
                        data=np.array(embedding).tobytes(),
                        tsne_x=0,
                        tsne_y=0,
                    )

                    db.session.add(new_embedding)

        try:
            db.session.commit()
            thread = threading.Thread(target=update_tsne_positions)
            thread.start()
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
                    "message": f"Successfully imported {len(channel['contents'])} notes",
                }
            ),
            201,
        )

    @app.route("/add-note", methods=["POST"])
    def add_note():
        new_note = Note(
            title="",
            user_id=TEST_ID,
            content=request.json["content"],
            hash="",
        )

        embedding = get_openai_embedding(request.json["content"])
        try:
            db.session.add(new_note)
            db.session.flush()
            if embedding is not None:
                new_embedding = Embedding(
                    user_id=TEST_ID,
                    note_id=new_note.note_id,
                    data=np.array(embedding).tobytes(),
                    tsne_x=0,
                    tsne_y=0,
                )

                db.session.add(new_embedding)

            db.session.commit()

            thread = threading.Thread(target=update_tsne_positions)
            thread.start()
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

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(use_reloader=True, port=5000, threaded=True)
