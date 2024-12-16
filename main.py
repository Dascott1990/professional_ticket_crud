from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import random
import string

app = Flask(__name__)

# Initialize database
def init_db():
    with sqlite3.connect("instance/tickets.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Not Started',
                progress INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()

init_db()

# Function to generate a secure 5-digit ticket ID
def generate_ticket_id():
    return ''.join(random.choices(string.digits, k=5))

# Home route
@app.route("/")
def home():
    with sqlite3.connect("instance/tickets.db") as conn:
        cursor = conn.cursor()
        # Fetch only the first 5 tickets
        cursor.execute("SELECT * FROM tickets LIMIT 5")
        tickets = cursor.fetchall()
    return render_template("index.html", tickets=tickets)

# Create ticket page
@app.route("/create-ticket", methods=["GET", "POST"])
def create_ticket():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        ticket_id = generate_ticket_id()

        with sqlite3.connect("instance/tickets.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tickets (id, title, description) VALUES (?, ?, ?)", (ticket_id, title, description))
            conn.commit()

        return redirect(url_for("view_tickets"))
    return render_template("create_ticket.html")

# View tickets page
@app.route("/view-tickets")
def view_tickets():
    with sqlite3.connect("instance/tickets.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets")
        tickets = cursor.fetchall()
    return render_template("view_tickets.html", tickets=tickets)

# Update ticket route (GET to show the form, POST to handle updates)
@app.route("/update-ticket/<ticket_id>", methods=["GET", "POST"])
def update_ticket(ticket_id):
    if request.method == "POST":
        # Handle form submission to update ticket
        new_status = request.form.get("status")
        new_progress = int(request.form.get("progress"))

        with sqlite3.connect("instance/tickets.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tickets SET status = ?, progress = ? WHERE id = ?",
                (new_status, new_progress, ticket_id)
            )
            conn.commit()

        return redirect(url_for("view_tickets"))

    else:
        # GET request to show the ticket update form with existing data
        with sqlite3.connect("instance/tickets.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
            ticket = cursor.fetchone()

        return render_template("update_ticket.html", ticket=ticket)

# Delete ticket (API endpoint)
@app.route("/delete-ticket/<ticket_id>", methods=["POST"])
def delete_ticket(ticket_id):
    with sqlite3.connect("instance/tickets.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        conn.commit()
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
