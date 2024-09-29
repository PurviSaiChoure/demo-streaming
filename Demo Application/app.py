from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
db_name = "india_disasters.db"

def get_db_connection():
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

# Get news data from the database
def get_news_data(topic=None, location=None, organization=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Basic query to retrieve data from disasters table
    query = "SELECT headline, description FROM disasters WHERE 1=1"

    # Add conditions based on the search filters
    params = []
    if topic:
        query += " AND headline LIKE ?"
        params.append(f'%{topic}%')
    if location:
        query += " AND description LIKE ?"
        params.append(f'%{location}%')
    if organization:
        query += " AND description LIKE ?"
        params.append(f'%{organization}%')

    # Execute the query with search filters
    cursor.execute(query, params)
    
    # Fetch top 8 results
    news_items = cursor.fetchall()[:8]
    conn.close()

    return [dict(item) for item in news_items]

@app.route('/')
def index():
    # Get search query parameters
    topic = request.args.get('topic')
    location = request.args.get('location')
    organization = request.args.get('organization')

    # Fetch news data based on search
    news_data = get_news_data(topic, location, organization)

    return render_template('index.html', news=news_data, enumerate=enumerate)

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
