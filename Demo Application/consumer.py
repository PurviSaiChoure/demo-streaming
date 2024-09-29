from kafka import KafkaConsumer, TopicPartition
import pandas as pd
from IPython.display import display, HTML
import json
import time
import sqlite3

kafka_nodes = "localhost:9092"
topic_name = "india_disasters"

db_name = "india_disasters.db"
table_name = "disasters"

news_list = []

def setup_database():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT,
            url TEXT,
            headline TEXT,
            description TEXT,
            persons TEXT,
            organizations TEXT,
            locations TEXT,
            dates TEXT,
            times TEXT,
            money TEXT,
            quantities TEXT,
            events TEXT,
            products TEXT,
            facilities TEXT,
            other_entities TEXT,
            author TEXT
        )
    ''')
    conn.commit()
    return conn, cursor

def insert_dataframe_to_database(conn, df):
    df.to_sql(table_name, conn, if_exists='replace', index=False)

def process_message(message):
    global news_list
    
    try:
        news_item = json.loads(message.value.decode('utf-8'))
        news_list.append(news_item)
        
        print("Received message:")
        for key, value in news_item.items():
            print(f"{key}: {value}")
        print("\n" + "-"*50 + "\n")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error processing message: {e}")

consumer = KafkaConsumer(
    bootstrap_servers=[kafka_nodes],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: x,  
    consumer_timeout_ms=10000
)

consumer.assign([TopicPartition(topic_name, 0)])

print("Starting to consume messages...")
start_time = time.time()
message_count = 0

try:
    while True:
        message_packet = consumer.poll(timeout_ms=1000)  
        for tp, messages in message_packet.items():
            for message in messages:
                process_message(message)
                message_count += 1
        
        if time.time() - start_time > 30 and len(message_packet) == 0:
            print("No new messages for 30 seconds. Stopping consumption.")
            break
except KeyboardInterrupt:
    print("Interrupted by user. Stopping consumption.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    consumer.close()

print(f"Total messages processed: {message_count}")

df = pd.DataFrame(news_list)

print("\nFinal DataFrame:")
if df.empty:
    print("No data received. DataFrame is empty.")
else:
    display(HTML(df.to_html()))

print("\nColumn names:")
print(df.columns.tolist())

print("\nColumn data types:")
print(df.dtypes)

print("\nSample data for each column:")
for column in df.columns:
    print(f"\n{column}:")
    print(df[column].head())

print("\nAdditional debug information:")
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")

if not df.empty:
    conn, cursor = setup_database()
    insert_dataframe_to_database(conn, df)
    print(f"Data inserted into the database. Total rows: {len(df)}")
    
    print("\nVerifying data in the database:")
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    db_count = cursor.fetchone()[0]
    print(f"Number of records in the database: {db_count}")
    
    conn.close()
else:
    print("No data to insert into the database.")

def view_database(db_name, table_name):
    conn = sqlite3.connect(db_name)
    
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    print(f"Table: {table_name}")
    print(f"Columns: {columns}")
    print(f"Total rows: {row_count}")
    
    query = f"SELECT * FROM {table_name} LIMIT 5"
    df = pd.read_sql_query(query, conn)
    print("\nFirst 5 rows:")
    print(df)
    
    conn.close()

print("\nViewing database contents:")
view_database(db_name, table_name)