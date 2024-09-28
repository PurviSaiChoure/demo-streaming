from bs4 import BeautifulSoup
import requests
from kafka import KafkaProducer
from json import dumps
import spacy

# Using NLP for categorisation
nlp = spacy.load('en_core_web_sm')

# URLs of news sites
ht_url = "https://timesofindia.indiatimes.com/topic/indian-disasters"
ndtv_url = "https://www.ndtv.com/search?searchtext=natural-disasters-in-india"
th_url = "https://www.thehindu.com/topic/Environmental_disasters_/"
urls = [ht_url, ndtv_url, th_url]
formats = ['html.parser', 'html.parser', 'html.parser']
website = ['Times of India', 'NDTV', 'The Hindu']
processed_urls = set()  # To track processed URLs and avoid duplicates

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}

# Kafka configuration
kafka_nodes = "localhost:9092"  
topic_name = "india_disasters"

def categorize_entities(ents):
    categorized = {
        'PERSON': [], 'ORG': [], 'GPE': [], 'DATE': [], 'TIME': [], 'MONEY': [],
        'QUANTITY': [], 'ORDINAL': [], 'CARDINAL': [], 'LOC': [], 'EVENT': [],
        'WORK_OF_ART': [], 'LAW': [], 'PRODUCT': [], 'FAC': []
    }
    for ent in ents:
        if ent.label_ in categorized:
            categorized[ent.label_].append(ent.text)
    return categorized

def gen_data():
    try:
        producer = KafkaProducer(
            bootstrap_servers=[kafka_nodes],
            value_serializer=lambda x: dumps(x).encode('utf-8')
        )
        
        for idx, url in enumerate(urls):
            print(f"Crawling web page: {url}")
            if website[idx] == "Times of India":
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url)
            
            soup = BeautifulSoup(response.content, formats[idx])
            
            # Processing for Times of India
            if website[idx] == "Times of India":
                articles = soup.find_all('div', class_='uwU81')
                for article in articles:
                    title_tag = article.find('div', class_='fHv_i o58kM')
                    link_tag = article.find('a')
                    if title_tag and link_tag:
                        headline = title_tag.get_text(strip=True)
                        article_url = "https://timesofindia.indiatimes.com" + link_tag['href']
                        if article_url not in processed_urls:
                            doc = nlp(headline)
                            entities = [(ent.text, ent.label_) for ent in doc.ents]
                            categorized_entities = categorize_entities(doc.ents)
                            
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
                            producer.send(topic_name, value=news_dict)
                            processed_urls.add(article_url)
                            print(f"Sent to Kafka: {news_dict}")
            
            # Processing for NDTV
            elif website[idx] == "NDTV":
                articles = soup.find_all('div', class_='src_itm-ttl')
                for article in articles:
                    title_tag = article.find('a')
                    if title_tag:
                        headline = title_tag.get_text(strip=True)
                        article_url = title_tag['href']
                        if article_url not in processed_urls:
                            doc = nlp(headline)
                            entities = [(ent.text, ent.label_) for ent in doc.ents]
                            categorized_entities = categorize_entities(doc.ents)
                            
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
                            producer.send(topic_name, value=news_dict)
                            processed_urls.add(article_url)
                            print(f"Sent to Kafka: {news_dict}")
            
            # Processing for The Hindu
            elif website[idx] == "The Hindu":
                articles = soup.find_all('div', class_='element row-element')  
                for article in articles:
                    title_element = article.find('h3', class_='title big')
                    author_element = article.find('div', class_='author-name')
                    url_element = title_element.find('a')

                    if title_element and url_element:
                        title = title_element.text.strip()
                        article_url = url_element['href']
                        author = author_element.text.strip() if author_element else "Unknown"

                        if article_url not in processed_urls:
                            doc = nlp(title)
                            entities = [(ent.text, ent.label_) for ent in doc.ents]
                            categorized_entities = categorize_entities(doc.ents)
                            
                            news_dict = {
                                'website': website[idx],
                                'url': article_url,
                                'headline': title,
                                'author': author,
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
                            producer.send(topic_name, value=news_dict)
                            processed_urls.add(article_url)
                            print(f"Sent to Kafka: {news_dict}")
        
        producer.flush()
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

gen_data()
