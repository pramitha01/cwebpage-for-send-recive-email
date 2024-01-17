from flask import Flask, render_template, request, session, redirect, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mailing_system'
mongo = PyMongo(app)

class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def save(self):
        mongo.db.users.insert_one({
            'username': self.username,
            'email': self.email
        })

    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({'email': email})

class Message:
    def __init__(self, sender_email, receiver_email, content):
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.content = content

    def save(self):
        mongo.db.messages.insert_one({
            'sender_email': self.sender_email,
            'receiver_email': self.receiver_email,
            'content': self.content
        })

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    if request.method == 'POST':
        sender_email = request.form['sender_email']
        receiver_email = request.form['receiver_email']
        message_content = request.form['message']

        sender = User.find_by_email(sender_email)
        receiver = User.find_by_email(receiver_email)

        if sender and receiver:
            message = f"Message from {sender['email']} to {receiver['email']} : {message_content}"
            saved_message = Message(sender_email=sender_email, receiver_email=receiver_email, content=message_content)
            saved_message.save()
            session['message'] = message  # Store message in session
            return redirect(url_for('index'))  # Redirect to clear form data after POST
        else:
            message = "User not found"
            session['message'] = message
            return redirect(url_for('index'))

    users = mongo.db.users.find()
    messages = mongo.db.messages.find()
    session_message = session.pop('message', None)

    return render_template('index.html', users=users, messages=messages, message=session_message)

if __name__ == '__main__':
    app.run(debug=True)