import os
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4
import re
from collections import Counter
from sqlalchemy import func
from textblob import TextBlob
from pathlib2 import Path

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.urandom(24)

db = SQLAlchemy(app)

class Emotion(db.Model):
    __tablename__ = 'Emotion'
    emotion_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sademotion = db.Column(db.Integer)
    happyemotion = db.Column(db.Integer)
    neutralemotion = db.Column(db.Integer)

class WordUsage(db.Model):
    __tablename__ = 'WordUsage'
    word_usage_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word1 = db.Column(db.String)
    word1count = db.Column(db.Integer)
    word2 = db.Column(db.String)
    word2count = db.Column(db.Integer)
    word3 = db.Column(db.String)
    word3count = db.Column(db.Integer)
    word4 = db.Column(db.String)
    word4count = db.Column(db.Integer)
    word5 = db.Column(db.String)
    word5count = db.Column(db.Integer)

class Weekly(db.Model):
    __tablename__ = 'Weekly'
    weekly_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sun = db.Column(db.Integer)
    mon = db.Column(db.Integer)
    tue = db.Column(db.Integer)
    wed = db.Column(db.Integer)
    thu = db.Column(db.Integer)
    fri = db.Column(db.Integer)
    sat = db.Column(db.Integer)

class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    longest_message = db.Column(db.String)
    word_usage_id = db.Column(db.Integer, db.ForeignKey('WordUsage.word_usage_id'))  # Change 'wordusage' to 'WordUsage'
    emotion_id = db.Column(db.Integer, db.ForeignKey('Emotion.emotion_id'))  # Adjust casing similarly

class Slideshow(db.Model):
    __tablename__ = 'Slideshow'
    slideshow_id = db.Column(db.String, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    theme = db.Column(db.String)
    weekly_id = db.Column(db.Integer, db.ForeignKey('Weekly.weekly_id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_slideshows')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_slideshows')
    winner = db.relationship('User', foreign_keys=[winner_id], backref='won_slideshows')
    weekly = db.relationship('Weekly', backref='slideshows')
User.emotion = db.relationship('Emotion')
User.word_usage = db.relationship('WordUsage')

with app.app_context():
    db.create_all()

def get_usernames(file_path):
    # Read the content of the file as a single string
    usernames = []
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        # Split the content into lines and extract usernames
        for line in file_content.split('\n'):
            parts = line.split('-')
            if len(parts) >= 2:
                username_part = parts[-1].split(':')
                username = username_part[0].strip()
                usernames.append(username)

    # Count the occurrences of each username
    username_counts = {}
    for username in usernames:
        username_counts[username] = username_counts.get(username, 0) + 1

    # Sort the dictionary by count values in descending order
    sorted_usernames = sorted(username_counts.items(), key=lambda x: x[1], reverse=True)

    # Select the top two usernames
    top_two_usernames = sorted_usernames[:2]
    usernames=[]
    usernames.append(top_two_usernames[0][0])
    usernames.append(top_two_usernames[1][0])
    return usernames

# Function to filter text file
def filter_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
    filtered_content = "\n".join(line.strip() for line in file_content.split("\n") if "<Media omitted>" not in line)
    with open(file_path, 'w', encoding='utf-8', errors='ignore') as file:
        file.write(filtered_content)

# Function to count messages for a user
def get_messages_count(file_path, target_user):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
    messages_count = sum(1 for line in file_content.split('\n') if f"- {target_user}:" in line)
    return messages_count

# Function to get the longest message for a user
def get_longest_message(file_path, username):
    longest_message = ""
    longest_length = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split(" - ")
            if len(parts) >= 2:
                message_parts = parts[-1].split(": ", 1)
                if len(message_parts) == 2:
                    message_sender = message_parts[0].strip()
                    if message_sender == username:
                        message = message_parts[1].strip()
                        message_length = len(message)
                        if message_length > longest_length:
                            longest_message = message
                            longest_length = message_length
    return longest_message

# Function for sentiment analysis
def sentiment_analysis(file_path, username):
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split(" - ")
            if len(parts) >= 2:
                message_parts = parts[-1].split(": ", 1)
                if len(message_parts) == 2:
                    message_sender = message_parts[0].strip()
                    if message_sender == username:
                        message = message_parts[1].strip()
                        blob = TextBlob(message)
                        polarity = blob.sentiment.polarity
                        if polarity > 0:
                            positive_count += 1
                        elif polarity < 0:
                            negative_count += 1
                        else:
                            neutral_count += 1

    total_count = positive_count + negative_count + neutral_count
    if total_count == 0:
        return 0, 0, 0
    else:
        positive_percentage = (positive_count / total_count) * 100
        negative_percentage = (negative_count / total_count) * 100
        neutral_percentage = (neutral_count / total_count) * 100
        return positive_percentage, negative_percentage, neutral_percentage

# Function to get most common words for a user
def get_most_common_words(file_path, username):
    user_words = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split(" - ")
            if len(parts) >= 2:
                message_parts = parts[-1].split(": ", 1)
                if len(message_parts) == 2:
                    message_sender = message_parts[0].strip()
                    if message_sender == username:
                        message = message_parts[1].strip()
                        words = re.findall(r'\b\w+\b', message.lower())
                        words = [word for word in words if len(word) > 3]
                        user_words.extend(words)

    word_counts = Counter(user_words)
    most_common_words = word_counts.most_common(5)
    return most_common_words

from datetime import datetime
from collections import Counter

def get_messages_per_day(file_path):
    messages_per_day = Counter()
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split(" - ")
            if len(parts) >= 2:
                # Extract the date and time from the message
                datetime_str = parts[0].strip()
                try:
                    datetime_obj = datetime.strptime(datetime_str, "%d/%m/%Y, %I:%M %p")
                    # Get the day of the week (0=Monday, 1=Tuesday, ..., 6=Sunday)
                    day_of_week = datetime_obj.weekday()
                    messages_per_day[day_of_week] += 1
                except:
                    None
    return messages_per_day

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=["POST"])
def upload():
    if request.method == 'POST':  
        f = request.files['file']  
        slideshow_ID = uuid4()  # Generate a unique ID
        unique_filename = str(slideshow_ID) + ".txt"
        f.save(unique_filename)
        # Extract names of persons from the file
        file_usernames = get_usernames(unique_filename)  
        # Pass the file name and slideshow ID to the themeselector.html template
        return render_template("themeselector.html", file_usernames=file_usernames, slideshow_ID=slideshow_ID)  
      
def replacetext(file_path, search_text, replace_text): 
    file = Path(file_path) 
    data = file.read_text(encoding='utf-8')  # Specify encoding as utf-8
    data = data.replace(search_text, replace_text) 
    file.write_text(data, encoding='utf-8')  # Specify encoding as utf-8

def replacetext2(file_path, search_text, replace_text): 
    file = Path(file_path) 
    data = file.read_text(encoding='utf-8')  # Specify encoding as utf-8
    data = data.replace(search_text, replace_text) 
    file.write_text(data, encoding='utf-8')  # Specify encoding as utf-8

@app.route('/confirm', methods=['POST'])
def confirm_names():
    slideshow_ID = request.form['slideshow_ID']

    theme = request.form.get('check-substitution-2')
    
    selected_sender_name = request.form['selected_sender_name']
    selected_recipient_name = request.form['selected_recipient_name']
    sender_name = request.form['sender_name']
    recipient_name = request.form['recipient_name']
    file_path = str(slideshow_ID) + ".txt"
    search1 = "m - " + selected_sender_name + ":"
    replace1 = "m - " + sender_name + ":"
    search2 = "m - " + selected_recipient_name + ":"
    replace2 = "m - " + recipient_name + ":"
    replacetext(file_path, search2, replace2)   
    replacetext(file_path, search1, replace1)  # Corrected line    


    # Process file for analytics
    total_message_count_sender = get_messages_count(file_path, sender_name)
    total_message_count_recipient = get_messages_count(file_path, recipient_name)
    longest_message_sender = len(get_longest_message(file_path, sender_name))
    longest_message_recipient = len(get_longest_message(file_path, recipient_name))
    sentiment_sender = sentiment_analysis(file_path, sender_name)
    sentiment_recipient = sentiment_analysis(file_path, recipient_name)
    common_words_sender = get_most_common_words(file_path, sender_name)
    common_words_recipient = get_most_common_words(file_path, recipient_name)
    messages_per_day_count = get_messages_per_day(file_path)

    query = db.insert(Emotion).values(sademotion=sentiment_sender[0], happyemotion=sentiment_sender[1], neutralemotion=sentiment_sender[2])
    db.session.execute(query)
    
    latest_word_usage_id = db.session.query(func.max(WordUsage.word_usage_id)).scalar()

    for index, (word, frequency) in enumerate(common_words_recipient, start=1):
        # Query the existing WordUsage row
        word_usage = WordUsage.query.get(latest_word_usage_id)
        if word_usage:
            # Update the corresponding column with the new values
            setattr(word_usage, f'word{index}', word)
            setattr(word_usage, f'word{index}count', frequency)
        else:
            # Handle the case where the WordUsage row doesn't exist
            print(f"WordUsage row with ID {latest_word_usage_id} not found.")
    db.session.execute(query)   

    sun = messages_per_day_count.get(0, 0) 
    mon = messages_per_day_count.get(1, 0) 
    tue = messages_per_day_count.get(2, 0) 
    wed = messages_per_day_count.get(3, 0) 
    thu = messages_per_day_count.get(4, 0) 
    fri = messages_per_day_count.get(5, 0) 
    sat = messages_per_day_count.get(6, 0) 

    query = db.insert(Weekly).values(sun =sun, mon =mon, tue=tue,wed=wed,thu=thu,fri =fri,sat =sat)
    db.session.execute(query)

    latest_word_usage_id = db.session.query(func.max(WordUsage.word_usage_id)).scalar()
    latest_emotion_id = db.session.query(func.max(Emotion.emotion_id)).scalar()

    query = db.insert(User).values(longest_message=longest_message_sender,word_usage_id=latest_word_usage_id,emotion_id=latest_emotion_id)
    db.session.execute(query)

    query = db.insert(Emotion).values(sademotion=sentiment_recipient[0], happyemotion=sentiment_recipient[1], neutralemotion=sentiment_recipient[2])
    db.session.execute(query)
    for index, (word, frequency) in enumerate(common_words_recipient, start=1):
        query = db.insert(WordUsage).values(
            **{
                f'word{index}': word,
                f'word{index}count': frequency
            }
        )
        db.session.execute(query)

    latest_word_usage_id = db.session.query(func.max(WordUsage.word_usage_id)).scalar()
    latest_emotion_id = db.session.query(func.max(Emotion.emotion_id)).scalar()

    query = db.insert(User).values(longest_message=longest_message_sender,word_usage_id=latest_word_usage_id,emotion_id=latest_emotion_id)
    db.session.execute(query)

    receiver_id  = db.session.query(func.max(User.user_id)).scalar()
    sender_id = db.session.query(func.max(User.user_id)).filter(User.user_id < receiver_id).scalar()

    latest_weekly_id  = db.session.query(func.max(Weekly.weekly_id )).scalar()


    def get_winner_id(sender_id, receiver_id):
        # Count the number of messages sent by the sender
        sender_message_count = db.session.query(func.count(Slideshow.slideshow_id)).filter(Slideshow.sender_id == sender_id).scalar()

        # Count the number of messages sent by the receiver
        receiver_message_count = db.session.query(func.count(Slideshow.slideshow_id)).filter(Slideshow.receiver_id == receiver_id).scalar()

        # Determine the winner based on the maximum number of messages
        if sender_message_count > receiver_message_count:
            return sender_id
        elif sender_message_count < receiver_message_count:
            return receiver_id
        else:
            return None
    
    query = db.insert(Slideshow).values(slideshow_id=slideshow_ID,sender_id=sender_id,receiver_id =receiver_id,theme =theme,weekly_id=latest_weekly_id,winner_id = get_winner_id(sender_id, receiver_id)  )
    db.session.execute(query)
    db.session.commit()
    os.remove(file_path)

    if theme=="Partner":
        renderFile="l1.html"
    else:
        renderFile="f1.html"
    
    return render_template(renderFile, 
        slideshow_ID=slideshow_ID, 
        sender_name=sender_name, 
        receiver_name=recipient_name,
        total_message_count_sender=total_message_count_sender,  
        total_message_count_recipient=total_message_count_recipient)


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
    
    
