import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_conn, init_db

app = Flask(__name__)
app.secret_key = os.environ.get("GINTERSHIPS_SECRET", "dev-only-change-me")

# clé : (nom affiché, mots-clés cherchés dans le titre)
INTERESTS = {
    "data":      ("Data & IA",              ["data", "machine learning", "intelligence artificielle", "analyst", "analytics", "business intelligence"]),
    "cyber":     ("Cybersécurité",          ["cyber", "security", "sécurité informatique", "pentest"]),
    "dev":       ("Développement & Web",    ["développeur", "developpeur", "developer", "web", "software", "full stack", "fullstack", "frontend", "backend", "informatique"]),
    "cloud":     ("Réseaux & Cloud",        ["cloud", "réseau", "reseau", "network", "devops", "télécom", "telecom"]),
    "iot":       ("IoT & Systèmes embarqués", ["iot", "embarqu", "embedded", "électronique", "electronique", "automatisme"]),
    "marketing": ("Marketing & Commercial", ["marketing", "communication", "commercial", "vente", "sales", "digital"]),
    "finance":   ("Finance & Comptabilité", ["comptab", "finance", "audit", "gestion", "account"]),
    "rh":        ("Ressources humaines",    ["ressources humaines", "rh", "human resources", "recrutement"]),
    "industrie": ("Industrie & Logistique", ["industri", "logisti", "maintenance", "production", "qualité", "supply", "mécanique", "génie", "ingénieur"]),
}

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Connecte-toi pour continuer.")
            return redirect(url_for("signin"))
        return f(*args, **kwargs)
    return wrapper

def offers_for(keys):
    kws = []
    for k in keys:
        if k in INTERESTS:
            kws += INTERESTS[k][1]
    if not kws:
        return []
    cond = " OR ".join(["LOWER(title) LIKE ?"] * len(kws))
    params = [f"%{k}%" for k in kws]
    conn = get_conn()
    rows = conn.execute(
        f"SELECT * FROM offers WHERE category='stage' AND ({cond}) ORDER BY id DESC", params
    ).fetchall()
    conn.close()
    return rows

@app.route("/")
def home():
    conn = get_conn()
    offers = conn.execute(
        "SELECT * FROM offers WHERE category = 'stage' ORDER BY id DESC LIMIT 60"
    ).fetchall()
    conn.close()
    return render_template("home.html", offers=offers)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        try:
            conn = get_conn()
            cur = conn.execute(
                "INSERT INTO users(name, email, password_hash) VALUES (?,?,?)",
                (name, email, generate_password_hash(password)),
            )
            conn.commit()
            session["user_id"] = cur.lastrowid
            session["user_name"] = name
            conn.close()
            flash("Compte créé ! Choisis maintenant tes centres d'intérêt.")
            return redirect(url_for("profile"))
        except sqlite3.IntegrityError:
            flash("Cet email est déjà inscrit. Connecte-toi.")
    return render_template("signup.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_conn()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("profile"))
        flash("Email ou mot de passe incorrect.")
    return render_template("signin.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    conn = get_conn()
    if request.method == "POST":
        chosen = request.form.getlist("interests")
        conn.execute("DELETE FROM interests WHERE user_id = ?", (session["user_id"],))
        for k in chosen:
            if k in INTERESTS:
                conn.execute("INSERT INTO interests(user_id, keyword) VALUES (?,?)", (session["user_id"], k))
        conn.commit()
        conn.close()
        flash("Profil enregistré !")
        return redirect(url_for("my_offers"))
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    chosen = [r["keyword"] for r in conn.execute(
        "SELECT keyword FROM interests WHERE user_id = ?", (session["user_id"],))]
    conn.close()
    return render_template("profile.html", user=user, interests=INTERESTS, chosen=chosen)

@app.route("/my-offers")
@login_required
def my_offers():
    conn = get_conn()
    chosen = [r["keyword"] for r in conn.execute(
        "SELECT keyword FROM interests WHERE user_id = ?", (session["user_id"],))]
    conn.close()
    offers = offers_for(chosen)
    labels = [INTERESTS[k][0] for k in chosen if k in INTERESTS]
    return render_template("my_offers.html", offers=offers, labels=labels)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
