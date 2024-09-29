import time
import schedule
from json import dumps
from kafka import KafkaProducer
import requests
from bs4 import BeautifulSoup
import spacy
import os

kafka_nodes = os.environ.get('KAFKA_SERVER', 'kafka:29092')  # Use environment variable with fallback
myTopic = "india_disasters"

# Load the spaCy model for entity extraction
nlp = spacy.load('en_core_web_sm')

# Define the URLs and parsing formats
urls = [
    "https://timesofindia.indiatimes.com/topic/indian-disasters",
    "https://www.ndtv.com/search?searchtext=natural-disasters-in-india",
    "https://www.thehindu.com/topic/Environmental_disasters_/"
]
formats = ['html.parser', 'html.parser', 'html.parser']
website = ["Times of India", "NDTV", "The Hindu"]

# Custom headers for Times of India request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}

# Set to store processed article URLs
processed_urls = set()

def categorize_entities(entities):
    entity_categories = {
        'PERSON': [], 'ORG': [], 'GPE': [], 'DATE': [], 'TIME': [],
        'MONEY': [], 'QUANTITY': [], 'ORDINAL': [], 'CARDINAL': [],
        'LOC': [], 'EVENT': [], 'WORK_OF_ART': [], 'LAW': [],
        'PRODUCT': [], 'FAC': []
    }
    
    for entity, entity_type in entities:
        if entity_type in entity_categories:
            entity_categories[entity_type].append(entity)
    
    return entity_categories

def gen_data():
    try:
        producer = KafkaProducer(bootstrap_servers=[kafka_nodes], 
                                 value_serializer=lambda x: dumps(x).encode('utf-8'),
                                 api_version=(0, 10, 1))  # Specify API version
        
        for idx, url in enumerate(urls):
            print(f"Crawling web page: {url}")
            if website[idx] == "Times of India":
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url)
            
            soup = BeautifulSoup(response.content, formats[idx])
            
            if website[idx] == "Times of India":
                articles = soup.find_all('div', class_='uwU81')
                for article in articles:
                    title_tag = article.find('div', class_='fHv_i o58kM')
                    description_tag = article.find('p', class_='oxXSK o58kM')
                    link_tag = article.find('a')
                    if title_tag and link_tag:
                        headline = title_tag.get_text(strip=True)
                        article_url = "https://timesofindia.indiatimes.com" + link_tag['href']
                        if article_url not in processed_urls:
                            entities = [(ent.text, ent.label_) for ent in nlp(headline).ents]
                            categorized_entities = categorize_entities(entities)
                            
                            news_dict = {
                                'website': website[idx],
                                'url': article_url,
                                'headline': headline,
                                'entities': entities,
                                'persons': categorized_entities['PERSON'],
                                'organizations': categorized_entities['ORG'],
                                'gpes': categorized_entities['GPE'],
                                'dates': categorized_entities['DATE'],
                                'times': categorized_entities['TIME'],
                                'money': categorized_entities['MONEY'],
                                'quantities': categorized_entities['QUANTITY'],
                                'ordinals': categorized_entities['ORDINAL'],
                                'cardinals': categorized_entities['CARDINAL'],
                                'locations': categorized_entities['LOC'],
                                'events': categorized_entities['EVENT'],
                                'works_of_art': categorized_entities['WORK_OF_ART'],
                                'laws': categorized_entities['LAW'],
                                'products': categorized_entities['PRODUCT'],
                                'facilities': categorized_entities['FAC']
                            }
                            producer.send(myTopic, value=news_dict)
                            processed_urls.add(article_url)
                            print(f"Sent to Kafka: {news_dict}")
            
            elif website[idx] == "NDTV":
                articles = soup.find_all('li', class_='src_lst-li')
                for article in articles:
                    title_element = article.find('div', class_='src_itm-ttl')
                    description_element = article.find('div', class_='src_itm-txt')
                    url_element = title_element.find('a') if title_element else None
                    if title_element and description_element and url_element:
                        headline = title_element.text.strip()
                        description = description_element.text.strip()
                        article_url = url_element['href']
                        if article_url not in processed_urls:
                            headline += f" - {description}"
                            entities = [(ent.text, ent.label_) for ent in nlp(headline).ents]
                            categorized_entities = categorize_entities(entities)
                            
                            news_dict = {
                                'website': website[idx],
                                'url': article_url,
                                'headline': headline,
                                'entities': entities,
                                'persons': categorized_entities['PERSON'],
                                'organizations': categorized_entities['ORG'],
                                'gpes': categorized_entities['GPE'],
                                'dates': categorized_entities['DATE'],
                                'times': categorized_entities['TIME'],
                                'money': categorized_entities['MONEY'],
                                'quantities': categorized_entities['QUANTITY'],
                                'ordinals': categorized_entities['ORDINAL'],
                                'cardinals': categorized_entities['CARDINAL'],
                                'locations': categorized_entities['LOC'],
                                'events': categorized_entities['EVENT'],
                                'works_of_art': categorized_entities['WORK_OF_ART'],
                                'laws': categorized_entities['LAW'],
                                'products': categorized_entities['PRODUCT'],
                                'facilities': categorized_entities['FAC']
                            }
                            producer.send(myTopic, value=news_dict)
                            processed_urls.add(article_url)
                            print(f"Sent to Kafka: {news_dict}")
            
            elif website[idx] == "The Hindu":
                articles = soup.find_all('div', class_='element row-element')
                for article in articles:
                    title_element = article.find('h3', class_='title big')
                    url_element = title_element.find('a') if title_element else None
                    if title_element and url_element:
                        headline = title_element.text.strip()
                        article_url = url_element['href']
                        if article_url not in processed_urls:
                            entities = [(ent.text, ent.label_) for ent in nlp(headline).ents]
                            categorized_entities = categorize_entities(entities)
                            
                            news_dict = {
                                'website': website[idx],
                                'url': article_url,
                                'headline': headline,
                                'entities': entities,
                                'persons': categorized_entities['PERSON'],
                                'organizations': categorized_entities['ORG'],
                                'gpes': categorized_entities['GPE'],
                                'dates': categorized_entities['DATE'],
                                'times': categorized_entities['TIME'],
                                'money': categorized_entities['MONEY'],
                                'quantities': categorized_entities['QUANTITY'],
                                'ordinals': categorized_entities['ORDINAL'],
                                'cardinals': categorized_entities['CARDINAL'],
                                'locations': categorized_entities['LOC'],
                                'events': categorized_entities['EVENT'],
                                'works_of_art': categorized_entities['WORK_OF_ART'],
                                'laws': categorized_entities['LAW'],
                                'products': categorized_entities['PRODUCT'],
                                'facilities': categorized_entities['FAC']
                            }
                            producer.send(myTopic, value=news_dict)
                            processed_urls.add(article_url)
                            print(f"Sent to Kafka: {news_dict}")
        
        producer.flush()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    gen_data()  # Run once immediately
    schedule.every(5).minutes.do(gen_data)  # Then run every 5 minutes
    
    while True:
        schedule.run_pending()
        time.sleep(1)