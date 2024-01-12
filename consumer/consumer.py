from threading import Thread
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewPartitions, NewTopic
from kafka.errors import KafkaError
import json
from math import exp
from math import pi
from dotenv import load_dotenv
from database import Database
from datetime import datetime
import os

load_dotenv()

def check_pending_cities(city):
    # To make sure the consumer is stateless, we do the check in the database
    database = Database("pendingCities")
    if database.find_one({"consumer_pending_cities": city}):
        return True
    # If the city is not in the database, add it (It's being processed)
    database.insert({"consumer_pending_cities": city})
    return False

def remove_pending_city(city):
    database = Database("pendingCities")
    if database.find_one({"consumer_pending_cities": city}):
        database.delete({"consumer_pending_cities": city})
    database.close()

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

def json_deserializer(data):
    return json.loads(data.decode("utf-8"))

# Function to calculate air density
def air_density(temp, pressure, humidity):
    """Temperature in Celsius, pressure in Pa, humidity in %"""
    """Returns air density in kg/m³"""
    Rs = 287.058  # Specific gas constant for dry air, J/(kg·K)
    temperature_kelvin = temp + 273.15  # Convert Celsius to Kelvin
    
    # Calculate the vapor pressure part
    vapor_pressure_part = humidity * exp((17.5043 * temp) / (241.2 + temp))
    
    # Calculate the density
    air_density = (pressure - 230.617 * vapor_pressure_part) / (Rs * temperature_kelvin)

    return air_density

# Function to calculate power of the éolienne  P = 1/2 x Rho x S x V³ x Cp
def calculate_power(wind_speed, temp, pressure, humidity=0):
    """Wind speed in m/s, temperature in Celsius, pressure in Pa, humidity in %"""
    """Returns power in W"""
    # Density of air
    rho = air_density(temp, pressure, humidity)
    # Area of the wind turbine (We suppose that the radius is 45m)
    S = pi * 45 ** 2 # We suppose that the radius is 45m (It's a common value for onshore/offshore wind turbines)
    # Power coefficient
    Cp = 0.4 # We suppose that the power coefficient is 0.4
    # Calculate power
    power = 0.5 * rho * S * wind_speed**3 * Cp

    return round(power, 2)

def send_to_kafka(city, wind_data):
    try:
        print("Data processed, sending to Kafka for " + city + "...", flush=True)
        # Send To All Partitions of the Topic "weather"
        partitions = producer.partitions_for('response')
        for partition in partitions:
            producer.send('response', value=wind_data, partition=partition)
        producer.flush()
    except KafkaError as e:
        print("Failed to send data to Kafka: ", flush=True)
        print(e)

def save_to_database(data):
    print("Data processed and sent, saving to database for " + data['city'] + "...", flush=True)
    # Before saving the data, change timestamp to datetime
    data['timestamp'] = datetime.fromisoformat(data['timestamp'])
    # Save the data to the database
    database = Database()
    # If the city is already in the database, delete it before inserting the new data
    if database.find_one({"city": data['city']}):
        print("Data for " + data['city'] + " already in database, deleting...", flush=True)
        database.delete({"city": data['city']})
    # Insert the data
    database.insert(data)
    print("Data for " + data['city'] + " saved to database", flush=True)
    database.close()

def group_by_day(data):
    # Group data by day
    grouped_data = {}
    for forecast in data:
        date = forecast['dt'].split(' ')[0]
        if date not in grouped_data:
            grouped_data[date] = []
        grouped_data[date].append(forecast)
    return grouped_data

def get_average(data, current_date):
    # Calculate the average of the data
    all_days_average = []
    for date in data:
        # Skip today's forecast
        if date == current_date:
            continue
        day_average = {
            "date": date,
            "temp": 0,
            "pressure": 0,
            "humidity": 0,
            "wind": {
                "speed": 0,
                "deg": 0,
                "gust": 0
            },
            "total_power": 0,
            "power_detail": []
        }
        for forecast in data[date]:
            day_average['temp'] += forecast['temp']
            day_average['pressure'] += forecast['pressure']
            day_average['humidity'] += forecast['humidity']
            day_average['wind']['speed'] += forecast['wind']['speed']
            day_average['wind']['deg'] += forecast['wind']['deg']
            if 'gust' in forecast['wind']:
                day_average['wind']['gust'] += forecast['wind']['gust']
            day_average['total_power'] += forecast['power']
            day_average['power_detail'].append({
                "time": forecast['dt'].split(' ')[1],
                "power": forecast['power']
            })
        day_average['temp'] = round(day_average['temp'] / len(data[date]), 2)
        day_average['pressure'] = round(day_average['pressure'] / len(data[date]), 2)
        day_average['humidity'] = round(day_average['humidity'] / len(data[date]), 2)
        day_average['wind']['speed'] = round(day_average['wind']['speed'] / len(data[date]), 2)
        day_average['wind']['deg'] = round(day_average['wind']['deg'] / len(data[date]), 2)
        if 'gust' in forecast['wind']:
            day_average['wind']['gust'] = round(day_average['wind']['gust'] / len(data[date]), 2)
        day_average['total_power'] = round(day_average['total_power'] / len(data[date]), 2)
        all_days_average.append(day_average)
    return all_days_average

def format_data(data):
    formatted_data = {
        "timestamp": data["timestamp"],
        "city": data["city"],
        "current": data["current"],
        "forecast": get_average(group_by_day(data["forecast"]), data["current"]["date"])
    }

    return formatted_data


# Function to process data
def process_data(data):
    print("****************************************************", flush=True)
    print("New data received, processing for " + data['city'] + "...", flush=True)
    # Check if the city is already being processed
    if check_pending_cities(data['city']):
        print("City " + data['city'] + " is already being processed, skipping...", flush=True)
        return
    # Calculate power for current weather and add it to the data dict
    data['current']['power'] = calculate_power(data['current']['wind']['speed'], data['current']['temp'], data['current']['pressure'], data['current']['humidity'])
    # Calculate power for forecast weather and add it to the data dict
    for forecast in data['forecast']:
        forecast['power'] = calculate_power(forecast['wind']['speed'], forecast['temp'], forecast['pressure'], forecast['humidity'])
    # Reformat the data to send it to the database
    data = format_data(data)
    # Send data to Kafka
    send_to_kafka(data['city'], data)
    save_to_database(data)
    # Remove the city from the pending cities database
    remove_pending_city(data['city'])
    print("Deleted pending city: " + data['city'], flush=True)


if __name__ == "__main__":
    try:
        # Connect to Kafka and create the topic if it doesn't exist
        bootstrap_servers = [os.getenv('KAFKA_BOOTSTRAP_SERVERS')]
        desired_num_partitions = os.getenv('KAFKA_NUM_PARTITIONS') == None and 2 or int(os.getenv('KAFKA_NUM_PARTITIONS'))
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        # Create the topic if it doesn't exist
        if 'weather' not in admin_client.list_topics():
            print("Creating topic 'weather'...", flush=True)
            topic_list = []
            topic_list.append(NewTopic(name="weather", num_partitions=desired_num_partitions, replication_factor=1))
            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            print("Topic 'weather' created with " + str(desired_num_partitions) + " partitions", flush=True)
        else:
            # Get the number of partitions
            print("Topic 'weather' already exists", flush=True)
            topic_metadata = admin_client.describe_topics(topics=['weather'])
            num_partitions = len(topic_metadata[0]['partitions'])
            topic_partitions = {'weather': NewPartitions(total_count=num_partitions+desired_num_partitions)}
            print("Adding " + str(desired_num_partitions) + " partitions to topic 'weather'...", flush=True)
            admin_client.create_partitions(topic_partitions)

        # Create the consumer and a producer for backend communication
        print("Starting consumer on " + bootstrap_servers[0] + "...", flush=True)
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=json_serializer)
        consumer = KafkaConsumer('weather', bootstrap_servers=bootstrap_servers, value_deserializer=json_deserializer, group_id="consumer")
        print("A producer has been started for backend communication, broker: " + bootstrap_servers[0], flush=True)
        print("Consumer started on topic 'weather' on broker: " + bootstrap_servers[0], flush=True)
        for message in consumer:
            Thread(target=process_data, args=(message.value,)).start()
    except KafkaError as e:
        print("Failed to connect to Kafka: ", flush=True)
        print(e)





