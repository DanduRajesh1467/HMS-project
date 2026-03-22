from flask import Flask, render_template, request, redirect, session
from db_config import get_db

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- Login ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()

        user = request.form["username"]
        pwd = request.form["password"]

        cur.execute("SELECT * FROM admin WHERE username=%s AND password=SHA2(%s,256)", (user, pwd))
        result = cur.fetchone()

        if result:
            session["user"] = user
            return redirect("/dashboard")
        else:
            return "Invalid login"

    return render_template("login.html")

# ---------- Dashboard ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM bookings")
    data = cur.fetchall()

    return render_template("dashboard.html", bookings=data)

# ---------- Add Booking ----------
@app.route("/add", methods=["POST"])
def add():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        INSERT INTO bookings (name, phone, room, type, checkin, checkout)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        request.form["name"],
        request.form["phone"],
        request.form["room"],
        request.form["type"],
        request.form["checkin"],
        request.form["checkout"]
    ))

    db.commit()
    return redirect("/dashboard")

# ---------- Bill ----------
@app.route("/bill/<room>")
def bill(room):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM bookings WHERE room=%s", (room,))
    b = cur.fetchone()

    prices = {"standard":1000,"deluxe":2000,"suite":3000}

    days = (b["checkout"] - b["checkin"]).days
    total = days * prices[b["type"]]

    return f"<h2>Total Bill: ₹{total}</h2>"

# ---------- Checkout ----------
@app.route("/checkout/<room>")
def checkout(room):
    db = get_db()
    cur = db.cursor()

    cur.execute("DELETE FROM bookings WHERE room=%s", (room,))
    db.commit()

    return redirect("/dashboard")

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
