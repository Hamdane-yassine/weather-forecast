from concurrent.futures import ThreadPoolExecutor
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from kafka.admin import KafkaAdminClient, NewPartitions, NewTopic
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
from database import Database
import json
import threading

load_dotenv()

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

def json_deserializer(data):
    return json.loads(data.decode("utf-8"))

def send_to_kafka(city, wind_data):
    try:
        print("Data filtered, sending to Kafka for " + city + "...", flush=True)
        producer.send('weather', value=wind_data)
        producer.flush()
    except KafkaError as e:
        print("Failed to send data to Kafka: ", flush=True)
        print(e)

def filter_data(city, weather_data):
    print("Filtering data for city: " + city, flush=True)
    current = weather_data['current_weather']
    forecast = weather_data['forecast']
    wind_data = {
        "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        "city": city,
        "current": {
            "wind": current['wind'],
            "temp": current['main']['temp'],
            "pressure": current['main']['pressure'] * 100, # Convert hPa to Pa for air density calculation in consumer
            "humidity": current['main']['humidity'] / 100, # Convert % to decimal for air density calculation in consumer
            "date": datetime.utcfromtimestamp(current['dt']).strftime('%Y-%m-%d %H:%M:%S').split(' ')[0]
        },
        "forecast": []
    }
    for forecast_data in forecast['list']:
        data = {
            "wind": forecast_data['wind'],
            "temp": forecast_data['main']['temp'],
            "pressure": forecast_data['main']['pressure'] * 100, # Convert hPa to Pa for air density calculation in consumer
            "humidity": forecast_data['main']['humidity'] / 100, # Convert % to decimal for air density calculation in consumer
            "dt": datetime.utcfromtimestamp(forecast_data['dt']).strftime('%Y-%m-%d %H:%M:%S')
        }
        wind_data['forecast'].append(data)
    return wind_data

def get_weather_data(lat, lon):
    print("Getting weather data for city: " + lat + ", " + lon, flush=True)
    api_key = os.getenv('WEATHER_API_KEY_1')
    current_weather_url = os.getenv('API_URL') + "/weather"
    forecast_url = os.getenv('API_URL') + "/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"
    }

    # Get the last used API key from the api_keys list
    with lock:
        api_key = api_keys.pop(0)
        params['appid'] = api_key
        api_keys.append(api_key)
    print("Trying with API key: " + params['appid'], flush=True)
    try:
        current_weather_response = requests.get(current_weather_url, params=params)
        forecast_response = requests.get(forecast_url, params=params)
        if current_weather_response.status_code == 200 and forecast_response.status_code == 200 and current_weather_response != None and forecast_response != None:
            print("Successfully got weather data for city: " + lat + ", " + lon, flush=True)
        else:
            print("Failed to get weather data for city: " + lat + ", " + lon, flush=True)
            print("Current weather response: " + str(current_weather_response.status_code), flush=True)
            print("Forecast response: " + str(forecast_response.status_code), flush=True)
            return None
    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        print("An exception occurred while trying to get weather data for city: ", flush=True)
        print(e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        return None
    
    current_weather_data = current_weather_response.json()
    forecast_data = forecast_response.json()

    return {
        "current_weather": current_weather_data,
        "forecast": forecast_data
    }

def check_pending_cities(city):
    # To make sure the producer is stateless, we do the check in the database
    database = Database()
    if database.find_one({"producer_pending_cities": city}):
        return True
    # If the city is not in the database, add it (It's being processed)
    database.insert({"producer_pending_cities": city})
    return False

def remove_pending_city(city):
    database = Database()
    if database.find_one({"producer_pending_cities": city}):
        database.delete({"producer_pending_cities": city})
    database.close()

def handle_request(message):
    print("****************************************************", flush=True)
    print("Received request for city: " + message.value['city'], flush=True)
    data = message.value
    city = data['city']
    lat = data['lat']
    lon = data['lon']
    if check_pending_cities(city):
        print("City already being processed: " + city, flush=True)
        return
    weather_data = get_weather_data(lat, lon)
    if weather_data == None:
        print("Failed to get weather data for city: " + city, flush=True)
        remove_pending_city(city)
        return
    filtered_data = filter_data(city, weather_data)
    send_to_kafka(city, filtered_data)
    remove_pending_city(city)
    print("Data sent to kafka and removed from pending list: " + city, flush=True)

if __name__ == "__main__":
    try:
        # Connect to Kafka and create the topic if it doesn't exist
        bootstrap_servers = [os.getenv('KAFKA_BOOTSTRAP_SERVERS')]
        desired_num_partitions = os.getenv('KAFKA_NUM_PARTITIONS') == None and 2 or int(os.getenv('KAFKA_NUM_PARTITIONS'))
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        # Create the topic if it doesn't exist
        if 'requests' not in admin_client.list_topics():
            print("Creating topic 'requests'...", flush=True)
            topic_list = []
            topic_list.append(NewTopic(name="requests", num_partitions=desired_num_partitions, replication_factor=1))
            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            print("Topic 'requests' created with " + str(desired_num_partitions) + " partitions", flush=True)
        else:
            # Get the number of partitions
            print("Topic 'requests' already exists", flush=True)
            topic_metadata = admin_client.describe_topics(topics=['requests'])
            num_partitions = len(topic_metadata[0]['partitions'])
            topic_partitions = {'requests': NewPartitions(total_count=num_partitions+desired_num_partitions)}
            print("Adding " + str(desired_num_partitions) + " partitions to topic 'requests'...", flush=True)
            admin_client.create_partitions(topic_partitions)
        
        # Start the producer and a consumer for backend communication
        print("Starting producer on " + bootstrap_servers[0] + "...", flush=True)
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=json_serializer)
        consumer = KafkaConsumer('requests', bootstrap_servers=bootstrap_servers, value_deserializer=json_deserializer, group_id="producer")
        print("Producer started on broker: " + bootstrap_servers[0], flush=True)
        print("A consumer has been started for backend communication, broker: " + bootstrap_servers[0], flush=True)
        # Get all api keys
        api_keys = []
        for key in os.environ:
            if key.startswith('WEATHER_API_KEY_'):
                api_keys.append(os.getenv(key))
        print("All API keys loaded: ", flush=True)
        print(api_keys, flush=True)
        # Create a lock for the api_keys list
        lock = threading.Lock()
        # Start the thread pool
        max_workers = os.getenv('PRODUCER_MAX_WORKERS') == None and 20 or int(os.getenv('PRODUCER_MAX_WORKERS'))
        executor = ThreadPoolExecutor(max_workers=max_workers)
        try:
            for message in consumer:
                # Submit tasks to the thread pool
                executor.submit(handle_request, message)
                print(f"Active threads: {threading.active_count()}", flush=True)
                print(f"Pending tasks: {executor._work_queue.qsize()}", flush=True)
        finally:
            # Shutdown the executor when done
            executor.shutdown(wait=True)
    except KafkaError as e:
        print("Failed to connect to Kafka: ", flush=True)
        print(e)


