from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
db_name = "india_disasters.db"

def get_db_connection():
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT headline FROM disasters WHERE headline LIKE ?", ('%' + keyword + '%',))
    results = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in results])

if __name__ == '__main__':
    app.run(debug=True)
