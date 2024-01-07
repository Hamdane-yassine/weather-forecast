from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
import json
import threading

env = load_dotenv()

pending_cities = []

def filter_data(weather_data):
    current = weather_data['current_weather']
    forecast = weather_data['forecast']
    wind_data = {
        "city": current['name'],
        "current": {
            "wind": current['wind'],
            "temp": current['main']['temp'],
            "pressure": current['main']['pressure'],
            "dt": datetime.utcfromtimestamp(current['dt']).strftime('%Y-%m-%d %H:%M:%S')
        },
        "forecast": []
    }
    for forecast_data in forecast['list']:
        data = {
            "wind": forecast_data['wind'],
            "temp": forecast_data['main']['temp'],
            "pressure": forecast_data['main']['pressure'],
            "dt": datetime.utcfromtimestamp(forecast_data['dt']).strftime('%Y-%m-%d %H:%M:%S')
        }
        wind_data['forecast'].append(data)
    return wind_data

def handle_request(message):
    data = json.loads(message.value.decode("utf-8"))
    city = data['city']
    lat = data['lat']
    lon = data['lon']
    if city in pending_cities:
        return
    pending_cities.append(city)
    weather_data = get_weather_data(lat, lon)
    filtered_data = filter_data(weather_data)
    send_to_kafka(city, filtered_data)
    pending_cities.remove(city)

def get_weather_data(lat, lon):
    api_key = os.getenv('WEATHER_API_KEY')
    current_weather_url = os.getenv('API_URL') + "/weather" + "?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + api_key + "&units=metric"
    forecast_url = os.getenv('API_URL') + "/forecast" + "?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + api_key + "&units=metric"
    
    current_weather_response = requests.get(current_weather_url)
    forecast_response = requests.get(forecast_url)

    if current_weather_response.status_code != 200 or forecast_response.status_code != 200:
        print("Failed to get weather data")
        return
    current_weather_data = current_weather_response.json()
    forecast_data = forecast_response.json()
    return {
        "current_weather": current_weather_data,
        "forecast": forecast_data
    }


def send_to_kafka(city, wind_data):
    try:
        producer.send('weather', key=city.encode(), value=json.dumps(wind_data).encode())
        producer.flush()
    except KafkaError:
        print("Failed to send data to Kafka")

try:
    bootstrap_servers = [os.getenv('KAFKA_BOOTSTRAP_SERVERS')]
    print(bootstrap_servers)
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
    consumer = KafkaConsumer('requests', bootstrap_servers=bootstrap_servers)
    for message in consumer:
        threading.Thread(target=handle_request, args=(message,)).start()
except KafkaError:
    print("Failed to connect to Kafka")