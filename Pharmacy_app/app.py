from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
DB = 'pharmacy.db'

# Create DB and table
def init_db():
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                rack_number INTEGER NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.route('/')
def index():
    search = request.args.get('search', '')
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        if search:
            cur.execute("SELECT * FROM medicines WHERE name LIKE ?", ('%' + search + '%',))
        else:
            cur.execute("SELECT * FROM medicines")
        medicines = cur.fetchall()
    return render_template('index.html', medicines=medicines, search=search)

@app.route('/add', methods=['GET', 'POST'])
def add():
    message = ''
    if request.method == 'POST':
        name = request.form['name']
        qty = int(request.form['quantity'])
        price = float(request.form['price'])
        rack_number = int(request.form['rack_number'])

        with sqlite3.connect(DB) as conn:
            cur = conn.cursor()
            # Check how many medicines are already in this rack
            cur.execute("SELECT COUNT(*) FROM medicines WHERE rack_number = ?", (rack_number,))
            count = cur.fetchone()[0]

            if count >= 10:
                # Toggle between True (auto move) or False (deny addition)
                auto_move = True
                if auto_move:
                    rack_number += 1
                    message = f"Rack full. Automatically moved to Rack #{rack_number}."
                else:
                    message = f"Cannot add. Rack #{rack_number} is full."
                    return render_template('add.html', message=message)

            # Insert into DB
            cur.execute(
                "INSERT INTO medicines (name, quantity, price, rack_number) VALUES (?, ?, ?, ?)",
                (name, qty, price, rack_number)
            )
            conn.commit()

        return redirect('/')
    return render_template('add.html', message=message)

@app.route('/update/<int:med_id>', methods=['GET', 'POST'])
def update(med_id):
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        if request.method == 'POST':
            name = request.form['name']
            qty = int(request.form['quantity'])
            price = float(request.form['price'])
            rack_number = int(request.form['rack_number'])
            cur.execute(
                "UPDATE medicines SET name=?, quantity=?, price=?, rack_number=? WHERE id=?",
                (name, qty, price, rack_number, med_id)
            )
            conn.commit()
            return redirect('/')
        cur.execute("SELECT * FROM medicines WHERE id=?", (med_id,))
        med = cur.fetchone()
    return render_template('update.html', med=med)

@app.route('/delete/<int:med_id>')
def delete(med_id):
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM medicines WHERE id=?", (med_id,))
        conn.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
