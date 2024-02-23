from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
# pip install flask flask_sqlalchemy psycopg2-binary
app = Flask(__name__, template_folder='./')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@34.163.172.208/new_database'
db = SQLAlchemy(app)

class Entry(db.Model):
    __tablename__ = 'new_database'

    entryid = db.Column(db.Integer, primary_key=True)
    inputdatetime = db.Column(db.DateTime, nullable=False)
    audiofilename = db.Column(db.Text, nullable=False)
    usermetadata = db.Column(db.JSON)
    preprocessedtext = db.Column(db.Text)
    alertmetadata = db.Column(db.JSON)

@app.route('/')
def home():
    entries = Entry.query.all()
    print(entries)
    return render_template('index.html', entries=entries)

if __name__ == '__main__':
    app.run(port=5001)
