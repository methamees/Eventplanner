from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook

# Initialize app
app = Flask(__name__)
app.secret_key = 'd6bc5641a5e7c5184aa594524c179cf6'

# DB configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Facebook OAuth configuration
facebook_blueprint = make_facebook_blueprint(
    client_id="425656537070861",
    client_secret="d6bc5641a5e7c5184aa594524c179cf6",
    redirect_to="facebook_login"  # Redirect to this route after login
)
app.register_blueprint(facebook_blueprint, url_prefix="/facebook_login")

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(150), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref='events')

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    user = db.relationship('User', backref='rsvps')
    event = db.relationship('Event', back_populates='rsvps')

Event.rsvps = db.relationship('RSVP', order_by=RSVP.id, back_populates='event')

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/facebook_login')
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    resp = facebook.get('/me?fields=id,name,email')
    user_info = resp.json()
    # Example: Display user's name after login
    return f"Welcome, {user_info['name']}!"

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)