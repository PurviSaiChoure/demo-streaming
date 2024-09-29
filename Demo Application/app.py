from flask import Flask, render_template, request, jsonify
import sqlite3
from collections import Counter

app = Flask(__name__)
db_name = "india_disasters.db"

def get_db_connection():
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def get_news_data(keyword=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT headline, description, locations, events, url, persons, organizations 
    FROM disasters 
    WHERE headline LIKE ? OR description LIKE ? OR locations LIKE ? 
    OR events LIKE ? OR persons LIKE ? OR organizations LIKE ?
    """
    params = ['%' + keyword + '%'] * 6 if keyword else ['%%'] * 6

    cursor.execute(query, params)

    news_items = cursor.fetchall()
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

    return {
        'disaster_data': dict(disaster_types.most_common(5)),  # Return top 5 disaster types
        'location_data': dict(locations.most_common(5))        # Return top 5 locations
    }

@app.route('/')
def index():
    keyword = request.args.get('keyword', '')
    news_data = get_news_data(keyword)
    chart_data = get_chart_data(news_data)

    return render_template('index.html', news=news_data, disaster_data=chart_data['disaster_data'], 
                           location_data=chart_data['location_data'], keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True)