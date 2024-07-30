# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import requests
import json
from bs4 import BeautifulSoup
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
import os
import re
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
CORS(app)

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv('OPENAI_API_KEY'),   
)

def read_urls(file_path):
    with open(file_path, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls if url.strip()]

def scrape_university_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    
    # Remove leading and trailing whitespace
    cleaned_text = text.strip()
    
    # Replace multiple spaces with a single space
    cleaned_text = re.sub(r' +', ' ', cleaned_text)
    
    # Replace multiple newlines with a single newline
    cleaned_text = re.sub(r'\n+', '\n', cleaned_text)
    
    return cleaned_text

def extract_events(text):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""
                            Extract academic events from the following text. For each event, provide:
                            1. event_name
                            2. date
                            3. topic (Mathematics, physics, computer science...)
                            4. type (conference, seminar, or lesson)
                            5. brief_description (if available)
                            6. location
                            answer only with in json format, follow this template:
                            **start of your answer**:
                            [
                                {{ "event_name": "Federated and Split Machine Learning in the Internet of Things", "date": "2024-09-15", "topic": "Computer Science", "type": "conference", "brief_description": "In this talk we discuss approaches for distributed machine learning (ML) in resource-constrained edge-supported Internet of Things (IoT) networks. Federated Learning (FL) and Split Learning (SL) are popular approaches in such wireless edge networks.", "location": "New York, NY" }},
                                {{ "event_name": "Data Science Seminar", "date": "2024-10-01", "topic": "Data Science", "type": "seminar", "brief_description": "Weekly data science talks",  "location": "San Francisco, CA" }},
                                {{ "event_name": "Detecting a late changepoint in the preferential attachment model", "date": "2024-11-05", "topic": "Mathematics", "type": "conference", "brief_description": "International mathematics symposium",  "location": "London, UK" }},
                                {{ "event_name": "Growth of Sobolev norms for a quantum fluid system", "date": "2024-09-20", "topic": "Physics", "type": "lesson", "brief_description": "I will discuss the existence of turbulent solutions to a quantum hydrodynamic (QHD) system, with periodic boundary conditions. A suitable nonlinear change of variables (the Madelung transform) formally connects the QHD system to a non-linear Schrödinger (NLS) equation, for which we can construct smooth solutions displaying arbitrarily large growth of Sobolev norms above the energy regularity level.",  "location": "Cambridge, MA"}},
                            ]
                            **end of your answer**
                            Text: {text[:5000]}
                            """
            }
        ],
        model="gpt-4o-mini",
        max_tokens=2000
    )
    json_string = response.choices[0].message.content.strip()
    return json.loads(json_string[7:-4]) # remove '''json .... '''

def event_exists(c, event):
    c.execute("SELECT 1 FROM events WHERE event_name = ? AND date = ? AND topic = ? AND type = ?",
              (event["event_name"], event["date"], event["topic"], event["type"]))
    return c.fetchone() is not None

def save_to_database(events, url):
    conn = sqlite3.connect('./events.db')
    c = conn.cursor()
    
    #c.execute('''CREATE TABLE IF NOT EXISTS events
    #             (event_name TEXT, date TEXT, topic TEXT, type TEXT, brief_description TEXT, location TEXT, link TEXT)''')
    
    for event in events:
        print("Checking event:", event['event_name'])
        if not event_exists(c, event):
            print("Saving to database")
            c.execute("INSERT INTO events (event_name, date, topic, type, brief_description, location, link) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (event["event_name"], event["date"], event["topic"], event["type"], event["brief_description"], event.get("location"), url))
        else:
            print("Event already exists")
    
    conn.commit()
    conn.close()
    


def scrape_events():
    print('Scraping and updating the database...')
    urls = read_urls('urls.txt')
    for url in urls:
        print(f'Scraping URL: {url}')
        page_content = scrape_university_page(url)
        extracted_events = extract_events(page_content)
        save_to_database(extracted_events, url)
    
    """events = [
        { "event_name": "AI Conference 2024", "date": "2024-09-15", "topic": "Computer Science", "type": "conference", "brief_description": "Annual AI research conference", "location": "New York, NY", "link": "https://www.aiconference2024.com" },
        { "event_name": "Data Science Seminar", "date": "2024-10-01", "topic": "Data Science", "type": "seminar", "brief_description": "Weekly data science talks",  "location": "San Francisco, CA", "link": "https://www.datascienceseminar.com" },
        { "event_name": "Mathematics Symposium", "date": "2024-11-05", "topic": "Mathematics", "type": "conference", "brief_description": "International mathematics symposium",  "location": "London, UK", "link": "https://www.mathsymposium.com" },
        { "event_name": "Physics Lecture Series", "date": "2024-09-20", "topic": "Physics", "type": "lesson", "brief_description": "Advanced topics in quantum mechanics",  "location": "Cambridge, MA", "link": "https://www.physicslectureseries.com" },
    ]
    
    save_to_database(events)"""
    
    return jsonify({"status": "success"})
    


@app.route('/events', methods=['GET'])
def get_events():
    conn = sqlite3.connect('./events.db') 
    c = conn.cursor()
    c.execute("SELECT event_name, date, topic, type, brief_description, location, link FROM events")
    events = c.fetchall()
    conn.close()
    
    # Convert the data to a list of dictionaries
    event_list = [
        {"event_name": row[0], "date": row[1], "topic": row[2], "type": row[3], "brief_description": row[4], "location": row[5], "link": row[6]}
        for row in events
    ]
    
    return jsonify(event_list)


# Schedule the scraping every 24 hours
scheduler = BackgroundScheduler()
scheduler.add_job(func=scrape_events, trigger="interval", hours=24)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Ensure the table is created before scraping and updating
conn = sqlite3.connect('events.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS events
            (event_name TEXT, date TEXT, topic TEXT, type TEXT, brief_description TEXT, location TEXT, link TEXT,
            UNIQUE(event_name, date, topic, type))''')
conn.commit()
conn.close()

with app.app_context():
    scrape_events()

if __name__ == '__main__':
    app.run(debug=True)