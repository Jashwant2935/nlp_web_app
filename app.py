

from flask import Flask,render_template,request,redirect
import sqlite3
from transformers import pipeline


app=Flask(__name__)

# Load spaCy model
# ner_pipeline = pipeline(
#     "ner",
#     model="dslim/bert-base-NER",
#     aggregation_strategy="simple"
# )


sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

conn=sqlite3.connect("users.db")
connection=conn.cursor()

connection.execute(
"""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
"""
)

conn.commit()
conn.close()


@app.route('/')
def index():
    return render_template('login.html')
@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/perform_register',methods=['POST','GET'])
def perform_register():

    if request.method == 'POST':

        name=request.form['username']
        email=request.form['email']
        password=request.form['password']

        conn=sqlite3.connect("users.db")
        cursor=conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",(email,)
        )
        user=cursor.fetchone()
        # if user exist already
        if user:

            conn.close()
            return render_template(
                'register.html',
                message="User already exists."

            )

        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name,email,password)
        )

        conn.commit()
        conn.close()

        return render_template('login.html',
                               message="Registration Successful. Please Login")


#CHECK DATA
# conn = sqlite3.connect("users.db")
# cursor = conn.cursor()
#
# cursor.execute("SELECT * FROM users")
#
# data = cursor.fetchall()
#
# print(data)
#
# conn.close()

@app.route('/perform_login', methods=['POST'])
def perform_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn=sqlite3.connect("users.db")
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?",
                       (email,password))
        user=cursor.fetchone()
        conn.close()
        if user:

            return  redirect('/profile')
        else:
            pass
    return render_template('login.html',
                           message="Login Unsuccessful. Please Login ")

@app.route('/profile',methods=['POST','GET'])
def profile():
    return render_template('profile.html')

@app.route('/ner')
def ner():
    return render_template('ner.html')


@app.route('/perform_ner', methods=['POST'])
def perform_ner():
    return render_template(
        'ner.html',
        message="NER feature temporarily disabled"
        )

    # result = ner_pipeline(text)

    # Better labels
    label_map = {
        "PER": "PERSON",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION"
    }

    entities = []

    for item in result:

        label = label_map.get(
            item['entity_group'],
            item['entity_group']
        )

        entities.append({
            'text': item['word'],
            'label': label
        })

    return render_template(
        'ner.html',
        entities=entities
    )
@app.route('/sentiment')
def sentiment():
    return render_template('sentiment.html')
@app.route('/perform_sentiment', methods=['POST'])
def perform_sentiment():
    text=request.form['text']
    if text == "":
        return render_template('sentiment.html', message="Please enter some text")
    result=sentiment_pipeline(text)
    sentiment=result[0]['label']
    score=round(result[0]['score'],2)
    return render_template(
        'sentiment.html',sentiment=sentiment,score=score)


if __name__ == "__main__":
    app.run(debug=True)