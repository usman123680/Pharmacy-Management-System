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
                price REAL NOT NULL
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
    if request.method == 'POST':
        name = request.form['name']
        qty = int(request.form['quantity'])
        price = float(request.form['price'])
        with sqlite3.connect(DB) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO medicines (name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
            conn.commit()
        return redirect('/')
    return render_template('add.html')

@app.route('/update/<int:med_id>', methods=['GET', 'POST'])
def update(med_id):
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        if request.method == 'POST':
            name = request.form['name']
            qty = int(request.form['quantity'])
            price = float(request.form['price'])
            cur.execute("UPDATE medicines SET name=?, quantity=?, price=? WHERE id=?", (name, qty, price, med_id))
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
