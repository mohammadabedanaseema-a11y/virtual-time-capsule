from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS capsules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        message TEXT,
        unlock_date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------

@app.route("/")
def index():
    return render_template("index.html")

# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute(
        "INSERT INTO users(username,email,password) VALUES(?,?,?)",
        (username,email,password))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email,password))

        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect("/dashboard")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
    "SELECT * FROM capsules WHERE user_id=?",
    (session["user_id"],))

    capsules = c.fetchall()
    conn.close()

    today = str(date.today())

    return render_template("dashboard.html",
                           capsules=capsules,
                           today=today)

# ---------------- CREATE CAPSULE ----------------

@app.route("/create", methods=["GET","POST"])
def create():

    if request.method == "POST":

        title = request.form.get("title")
        message = request.form.get("message")
        unlock_date = request.form.get("unlock_date")

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute(
        "INSERT INTO capsules(user_id,title,message,unlock_date) VALUES(?,?,?,?)",
        (session["user_id"],title,message,unlock_date))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("create.html")

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)