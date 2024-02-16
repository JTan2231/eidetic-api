from flask import Flask, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text

app = Flask(__name__, static_folder='build', static_url_path='/')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://yangnet:yangnetpass@localhost/yangnet'

db = SQLAlchemy(app)

class Paper(db.Model):
    paper_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    abstract = db.Column(Text)
    publication_date = db.Column(db.Date)

@app.route('/papers')
def get_papers():
    papers = Paper.query.all()
    papers_list = []
    for paper in papers:
        papers_list.append({
            'paper_id': paper.paper_id,
            'title': paper.title,
            'abstract': paper.abstract,
            'publication_date': paper.publication_date.isoformat() if paper.publication_date else None
        })

    return jsonify(papers_list)

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(use_reloader=True, port=5000, threaded=True)

