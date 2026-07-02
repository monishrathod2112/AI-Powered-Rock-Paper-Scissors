from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# -----------------------------
# Game History Model
# -----------------------------
class GameHistory(db.Model):

    __tablename__ = "game_history"

    id = db.Column(db.Integer, primary_key=True)

    player_choice = db.Column(db.String(20), nullable=False)

    ai_choice = db.Column(db.String(20), nullable=False)

    winner = db.Column(db.String(50), nullable=False)

    difficulty = db.Column(db.String(20), nullable=False)

    user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
    nullable=False
)

# -----------------------------
# User Model
# -----------------------------
from flask_login import UserMixin

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    profile_image = db.Column(
        db.String(255),
        default="Monish.jpeg"
    )

    joined_on = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    bio = db.Column(
        db.String(300),
        default="Hello! I'm using AI RPS."
    )

    games = db.relationship(
        "GameHistory",
        backref="user",
        lazy=True
    )