import sqlite3
from getpass import getpass
#new
# Connect to SQLite3 database (creates if not exists)
conn = sqlite3.connect("event_system.db")
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    is_admin INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date TEXT,
    location TEXT,
    seats_available INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(event_id) REFERENCES events(id)
)
''')

conn.commit()


# ------------------- User Functionalities -------------------

def register():
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("✅ Registered successfully!")
    except:
        print("❌ Username already exists.")


def login():
    username = input("Username: ")
    password = getpass("Password: ")
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        print(f"\n✅ Welcome, {username}!")
        if user[3] == 1:
            admin_panel(user)
        else:
            user_panel(user)
    else:
        print("❌ Invalid login!")


# ------------------- Admin Panel -------------------

def admin_panel(admin_user):
    while True:
        print("\n--- Admin Panel ---")
        print("1. Add Event")
        print("2. Edit Event")
        print("3. Delete Event")
        print("4. View All Events")
        print("5. Logout")
        choice = input("Choose: ")

        if choice == '1':
            name = input("Event Name: ")
            date = input("Event Date (YYYY-MM-DD): ")
            location = input("Location: ")
            seats = int(input("Seats Available: "))
            cursor.execute("INSERT INTO events (name, date, location, seats_available) VALUES (?, ?, ?, ?)",
                           (name, date, location, seats))
            conn.commit()
            print("✅ Event added.")

        elif choice == '2':
            event_id = input("Enter Event ID to edit: ")
            name = input("New Event Name: ")
            date = input("New Date: ")
            location = input("New Location: ")
            seats = int(input("New Seats Available: "))
            cursor.execute("UPDATE events SET name=?, date=?, location=?, seats_available=? WHERE id=?",
                           (name, date, location, seats, event_id))
            conn.commit()
            print("✅ Event updated.")

        elif choice == '3':
            event_id = input("Enter Event ID to delete: ")
            cursor.execute("DELETE FROM events WHERE id=?", (event_id,))
            conn.commit()
            print("🗑️ Event deleted.")

        elif choice == '4':
            view_events()

        elif choice == '5':
            break
        else:
            print("Invalid choice.")


# ------------------- User Panel -------------------

def user_panel(user):
    while True:
        print("\n--- User Menu ---")
        print("1. View Events")
        print("2. Book Ticket")
        print("3. My Tickets")
        print("4. Logout")
        choice = input("Choose: ")

        if choice == '1':
            view_events()

        elif choice == '2':
            event_id = input("Enter Event ID to book: ")
            # Check if seats are available
            cursor.execute("SELECT seats_available FROM events WHERE id=?", (event_id,))
            event = cursor.fetchone()
            if event and event[0] > 0:
                cursor.execute("INSERT INTO tickets (user_id, event_id) VALUES (?, ?)", (user[0], event_id))
                cursor.execute("UPDATE events SET seats_available = seats_available - 1 WHERE id=?", (event_id,))
                conn.commit()
                print("🎟️ Ticket booked!")
            else:
                print("❌ No seats available or invalid event.")

        elif choice == '3':
            cursor.execute('''
                SELECT events.name, events.date, events.location
                FROM tickets
                JOIN events ON tickets.event_id = events.id
                WHERE tickets.user_id=?
            ''', (user[0],))
            bookings = cursor.fetchall()
            print("\n--- Your Booked Tickets ---")
            for b in bookings:
                print(f"📅 {b[0]} | {b[1]} | 📍 {b[2]}")

        elif choice == '4':
            break

        else:
            print("Invalid choice.")


# ------------------- View Events -------------------

def view_events():
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    print("\n--- Event Listings ---")
    for e in events:
        print(f"ID: {e[0]} | {e[1]} | 📅 {e[2]} | 📍 {e[3]} | Seats Left: {e[4]}")


# ------------------- Seed Admin Account -------------------

def seed_admin():
    cursor.execute("SELECT * FROM users WHERE is_admin=1")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES ('admin', 'admin123', 1)")
        conn.commit()


# ------------------- Main Loop -------------------

def main():
    seed_admin()
    while True:
        print("\n=== College Event Management System ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose: ")
        if choice == '1':
            register()
        elif choice == '2':
            login()
        elif choice == '3':
            break
        else:
            print("Invalid choice.")


main()
conn.close()
