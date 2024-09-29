from flask import Flask, render_template, request, jsonify
import sqlite3
from collections import Counter

app = Flask(__name__)  # Corrected here
db_name = "india_disasters.db"

def get_db_connection():
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def get_news_data(topic=None, location=None, organization=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT headline, description, locations, events, url FROM disasters WHERE 1=1"
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

    cursor.execute(query, params)

    news_items = cursor.fetchall()[:8]
    conn.close()

    return [dict(item) for item in news_items]

def get_chart_data(news_data):
    disaster_types = Counter()
    locations = Counter()

    for item in news_data:
        if item['events']:
            disaster_types.update(item['events'].split(', '))
        if item['locations']:
            locations.update(item['locations'].split(', '))

    # Create a more detailed return structure for the charts
    return {
        'disaster_data': dict(disaster_types.most_common()),  # Return all disaster types
        'location_data': dict(locations.most_common())         # Return all locations
    }

@app.route('/')
def index():
    topic = request.args.get('topic')
    location = request.args.get('location')
    organization = request.args.get('organization')

    news_data = get_news_data(topic, location, organization)
    chart_data = get_chart_data(news_data)

    # Pass chart_data to the template for use in the frontend
    return render_template('index.html', news=news_data, disaster_data=chart_data['disaster_data'], location_data=chart_data['location_data'], enumerate=enumerate)

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT headline, description, url FROM disasters WHERE headline LIKE ?", ('%' + keyword + '%',))
    results = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in results])

if __name__ == '__main__':  # Corrected here
    app.run(debug=True)
