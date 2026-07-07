print("HELLO MONISH")

import os
import uuid
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
import random
import time
import csv
from flask_mail import Mail, Message
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    Response,
    redirect,
    flash,
    session,
    url_for,
    abort
)
from config import Config
from models.database import db, GameHistory, User
import random
from collections import Counter
from ml.predict import predict_next_move
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
import re

def allowed_file(filename):

    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
app.secret_key = "monish_secret_key"

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

# Initialize Database
db.init_app(app)

# Create Database Tables
with app.app_context():
    db.create_all()
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

# AI Choices
choices = ["rock", "paper", "scissors"]
otp_storage = {}

# -----------------------------
# Winner Logic
# -----------------------------
def find_winner(player, ai):

    if player == ai:
        return "Draw"

    if (
        (player == "rock" and ai == "scissors") or
        (player == "paper" and ai == "rock") or
        (player == "scissors" and ai == "paper")
    ):
        return "Player Wins 🎉"

    return "AI Wins 🤖"


# -----------------------------
# AI Prediction
# -----------------------------
def ai_prediction(difficulty):
    
    # Easy Mode
    if difficulty == "easy":
        return random.choice(choices)

    # Medium Mode
    if difficulty == "medium":

      if random.randint(1, 100) <= 50:
            return random.choice(choices)

    # Hard Mode (Machine Learning)

    history = GameHistory.query.order_by(
        GameHistory.id.desc()
    ).limit(1).all()

    # Agar history nahi hai to random
    if len(history) == 0:
        return random.choice(choices)

    last_move = history[0].player_choice

    predicted_move = predict_next_move(last_move)

    # Counter Move
    if predicted_move == "rock":
        return "paper"

    elif predicted_move == "paper":
        return "scissors"

    else:
        return "rock"

# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------------------
# Register
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        confirm_password = request.form["confirm_password"]

        if password != confirm_password:

            flash("Passwords do not match!", "danger")

            return redirect("/register")
        
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect("/register")

        if not re.search(r"[A-Z]", password):
            flash("Password must contain an uppercase letter.", "danger")
            return redirect("/register")

        if not re.search(r"[a-z]", password):
            flash("Password must contain a lowercase letter.", "danger")
            return redirect("/register")

        if not re.search(r"\d", password):
            flash("Password must contain a number.", "danger")
            return redirect("/register")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            flash("Password must contain a special character.", "danger")
            return redirect("/register")
        
        # Check if email already exists
        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already registered!", "danger")
            return redirect("/register")

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful! Please Login.", "success")
        return redirect("/login")

    return render_template("register.html")

# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        remember = "remember" in request.form

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user, remember=remember)

            flash("Login Successful!", "success")

            return redirect("/dashboard")

        flash("Invalid Email or Password", "danger")

        return redirect("/login")

    return render_template("login.html")

# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully!", "info")

    return redirect("/")

# -----------------------------
# Game Page
# -----------------------------
@app.route("/game")
def game():
    return render_template("game.html")


# -----------------------------
# Test Route
# -----------------------------
@app.route("/test")
def test():
    return "Flask is Working!"


# -----------------------------
# Play Route
# -----------------------------
@app.route("/play", methods=["POST"])
@login_required
def play():

    data = request.get_json()

    player = data["choice"]
    difficulty = data["difficulty"]

    # SMART AI
    ai = ai_prediction(difficulty)

    winner = find_winner(player, ai)

    # Save Match
    game = GameHistory(
        player_choice=player,
        ai_choice=ai,
        winner=winner,
        difficulty=difficulty,
        user_id=current_user.id
    )

    db.session.add(game)
    db.session.commit()

    return jsonify({
        "player": player,
        "ai": ai,
        "winner": winner
    })

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    view = request.args.get("view", "all")
    base_query = GameHistory.query
    if view == "user":
        base_query = base_query.filter_by(user_id=current_user.id)

    total_games = base_query.count()

    player_wins = base_query.filter_by(
        winner="Player Wins 🎉"
    ).count()

    ai_wins = base_query.filter_by(
        winner="AI Wins 🤖"
    ).count()

    draws = base_query.filter_by(
        winner="Draw"
    ).count()

    if total_games > 0:
        ai_accuracy = round((ai_wins / total_games) * 100, 2)
        player_accuracy = round((player_wins / total_games) * 100, 2)
    else:
        ai_accuracy = 0
        player_accuracy = 0

    winner = request.args.get("winner")
    difficulty = request.args.get("difficulty")

    query = base_query

    if winner:
        query = query.filter(
            GameHistory.winner.contains(winner)
        )

    if difficulty:
        query = query.filter_by(
            difficulty=difficulty
        )

    games = query.order_by(
        GameHistory.id.desc()
    ).all()

    player_streak = 0
    best_player_streak = 0

    ai_streak = 0
    best_ai_streak = 0

    for game in games:

        if game.winner == "Player Wins 🎉":

            player_streak += 1
            ai_streak = 0

            if player_streak > best_player_streak:
                best_player_streak = player_streak

        elif game.winner == "AI Wins 🤖":

            ai_streak += 1
            player_streak = 0

            if ai_streak > best_ai_streak:
                best_ai_streak = ai_streak

        else:

            player_streak = 0
            ai_streak = 0

    easy_games = base_query.filter_by(
        difficulty="easy"
    ).count()

    medium_games = base_query.filter_by(
        difficulty="medium"
    ).count()

    hard_games = base_query.filter_by(
        difficulty="hard"
    ).count()

# -----------------------------
# Player Move Analytics
# -----------------------------
    rock_count = base_query.filter_by(
        player_choice="rock"
    ).count()

    paper_count = base_query.filter_by(
        player_choice="paper"
    ).count()

    scissors_count = base_query.filter_by(
        player_choice="scissors"
    ).count()

# -----------------------------
# AI Move Analytics
# -----------------------------
    ai_rock_count = base_query.filter_by(
        ai_choice="rock"
    ).count()

    ai_paper_count = base_query.filter_by(
        ai_choice="paper"
    ).count()

    ai_scissors_count = base_query.filter_by(
        ai_choice="scissors"
    ).count()

    chart_labels = []
    chart_data = []

    for i, game in enumerate(games, start=1):
        chart_labels.append(i)
        chart_data.append(i)

    return render_template(
        "dashboard.html",
        view=view,
        total_games=total_games,
        player_wins=player_wins,
        ai_wins=ai_wins,
        draws=draws,
        ai_accuracy=ai_accuracy,
        player_accuracy=player_accuracy,
        games=games,
        chart_labels=chart_labels,
        chart_data=chart_data,
        easy_games=easy_games,
        medium_games=medium_games,
        hard_games=hard_games,
        player_streak=player_streak,
        best_player_streak=best_player_streak,
        ai_streak=ai_streak,
        best_ai_streak=best_ai_streak,
        rock_count=rock_count,
        paper_count=paper_count,
        scissors_count=scissors_count,
        ai_rock_count=ai_rock_count,
        ai_paper_count=ai_paper_count,
        ai_scissors_count=ai_scissors_count,
        )

# -----------------------------
# Profile
# -----------------------------
@app.route("/profile")
@login_required
def profile():

    total_games = GameHistory.query.filter_by(
        user_id=current_user.id
    ).count()

    player_wins = GameHistory.query.filter_by(
        user_id=current_user.id,
        winner="Player Wins 🎉"
    ).count()

    ai_wins = GameHistory.query.filter_by(
        user_id=current_user.id,
        winner="AI Wins 🤖"
    ).count()

    draws = GameHistory.query.filter_by(
        user_id=current_user.id,
        winner="Draw"
    ).count()

    if total_games > 0:
        win_rate = round((player_wins / total_games) * 100, 2)
    else:
        win_rate = 0

    return render_template(
        "profile.html",
        total_games=total_games,
        player_wins=player_wins,
        ai_wins=ai_wins,
        draws=draws,
        win_rate=win_rate
    )

# -----------------------------
# Change Password
# -----------------------------
@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form["current_password"]

        new_password = request.form["new_password"]

        confirm_password = request.form["confirm_password"]

        if not check_password_hash(
            current_user.password,
            current_password
        ):

            flash(
                "Current password is incorrect!",
                "danger"
            )

            return redirect("/change-password")

        if new_password != confirm_password:

            flash(
                "Passwords do not match!",
                "danger"
            )

            return redirect("/change-password")

        current_user.password = generate_password_hash(
            new_password
        )

        db.session.commit()

        flash(
            "Password changed successfully!",
            "success"
        )

        return redirect("/profile")

    return render_template("change_password.html")

# -----------------------------
# Delete Account
# -----------------------------
@app.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    # Delete all game history for the user
    GameHistory.query.filter_by(user_id=current_user.id).delete()
    # Delete the user record
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    flash("Your account has been deleted.", "success")
    return redirect(url_for('home'))

# -----------------------------
# Edit Profile
# -----------------------------
@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():

    if request.method == "POST":

        existing_user = User.query.filter_by(
        username=request.form["username"]).first()

        if existing_user and existing_user.id != current_user.id:

            flash("Username already exists!", "danger")

            return redirect("/edit-profile")

        current_user.username = request.form["username"]

        existing_user = User.query.filter_by(
        email=request.form["email"]).first()

        if existing_user and existing_user.id != current_user.id:

            flash("Email already exists!", "danger")

            return redirect("/edit-profile")

        current_user.email = request.form["email"]

        current_user.bio = request.form["bio"]

        image = request.files.get("profile_image")

        if image and image.filename != "":

            if not allowed_file(image.filename):

                flash(
                    "Only PNG, JPG and JPEG files are allowed.",
                    "danger"
                )

                return redirect("/edit-profile")

            extension = image.filename.rsplit(".", 1)[1].lower()

            filename = f"{uuid.uuid4()}.{extension}"

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            if current_user.profile_image != "default.png":

                old_image = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    current_user.profile_image
                )

                if os.path.exists(old_image):

                    os.remove(old_image)

            current_user.profile_image = filename

        db.session.commit()

        flash("Profile Updated Successfully!", "success")

        return redirect("/profile")

    return render_template("edit_profile.html")

# -----------------------------
# Export CSV
# -----------------------------
@app.route("/export")
def export_csv():

    print("EXPORT ROUTE CALLED") 
    games = GameHistory.query.all()

    output = "ID,Player Choice,AI Choice,Winner,Difficulty\n"

    for game in games:
        output += (
            f"{game.id},"
            f"{game.player_choice},"
            f"{game.ai_choice},"
            f"{game.winner},"
            f"{game.difficulty}\n"
        )

    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=match_history.csv"
        }
    )

# -----------------------------
# Forgot Password
# -----------------------------
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        user = User.query.filter_by(email=email).first()

        if not user:

            flash("Email not found!", "danger")

            return redirect("/forgot-password")

        otp = random.randint(100000, 999999)

        otp_storage[email] = {
            "otp": str(otp),
            "time": time.time()
        }

        msg = Message(
            "AI RPS Password Reset OTP",
            sender=app.config["MAIL_USERNAME"],
            recipients=[email]
        )

        msg.body = f"""
Hello,

Your OTP is: {otp}

This OTP is valid for 5 minutes.

Regards,
AI RPS Team
"""

        print(f"GENERATED_OTP_FOR_TESTING: {otp}")
        mail.send(msg)

        # Store email in session for subsequent steps
        session["reset_email"] = email

        flash("OTP sent successfully! Check your email.", "success")

        return redirect("/verify-otp")

    return render_template("forgot_password.html")

# -----------------------------
# Verification OTP
# -----------------------------
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    email = session.get("reset_email")
    if not email:
        flash("No active password reset request found. Please start here.", "danger")
        return redirect("/forgot-password")

    if request.method == "POST":
        otp = request.form["otp"]

        if email not in otp_storage:
            flash("OTP session not found. Please request a new OTP.", "danger")
            return redirect("/forgot-password")

        # OTP Expiry (5 minutes)
        if time.time() - otp_storage[email]["time"] > 300:
            del otp_storage[email]
            session.pop("reset_email", None)
            flash("OTP Expired!", "danger")
            return redirect("/forgot-password")

        # OTP Verify
        if otp_storage[email]["otp"] == otp:
            # Set flag indicating OTP is verified
            session["otp_verified"] = True
            flash("OTP Verified Successfully! Set your new password.", "success")
            return redirect("/reset-password")

        flash("Invalid OTP! Please try again.", "danger")
        return redirect("/verify-otp")

    return render_template("verify_otp.html")

# -----------------------------
# user database check whether how many user are login 
# -----------------------------

@app.route("/users")
def users():

    users = User.query.all()

    for user in users:
        print(user.username, user.email)

    return f"Total Users: {len(users)}"

# -----------------------------
# Reset Password
# -----------------------------
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = session.get("reset_email")
    otp_verified = session.get("otp_verified")

    if not email or not otp_verified:
        flash("Unauthorized access. Please request and verify OTP first.", "danger")
        return redirect("/forgot-password")

    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect("/reset-password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found!", "danger")
            return redirect("/forgot-password")

        user.password = generate_password_hash(password)
        db.session.commit()

        # Clean up session and storage on successful reset
        if email in otp_storage:
            del otp_storage[email]
        session.pop("reset_email", None)
        session.pop("otp_verified", None)

        flash("Password reset successful! Please log in.", "success")
        return redirect("/login")

    return render_template("reset_password.html")

# -----------------------------
# Leaderboard
# -----------------------------
@app.route("/leaderboard")
@login_required
def leaderboard():

    search = request.args.get("search", "")

    query = db.session.query(

        User.id,

        User.username,

        User.profile_image,

        db.func.count(GameHistory.id).label("games"),

        db.func.sum(
            db.case(
                (GameHistory.winner == "Player Wins 🎉", 1),
                else_=0
            )
        ).label("wins")

    ).outerjoin(

        GameHistory,
        User.id == GameHistory.user_id

    )

    if search:

        query = query.filter(
            User.username.ilike(f"%{search}%")
        )

    leaderboard = query.group_by(
        User.id
    ).order_by(
        db.func.sum(
            db.case(
                (GameHistory.winner == "Player Wins 🎉", 1),
                else_=0
            )
        ).desc()
    ).all()

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard,
        search=search
    )


# -----------------------------
# Developer Debug OTP Endpoint
# -----------------------------
@app.route("/test-otp")
def test_otp():
    return jsonify(otp_storage)

# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)