from threading import Thread
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import json
from math import exp
from math import pi
from dotenv import load_dotenv
import os

env = load_dotenv()

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
    return power

# Function to process data
def process_data(data):
    # Calculate power for current weather and add it to the data dict
    data['current']['power'] = calculate_power(data['current']['wind']['speed'], data['current']['temp'], data['current']['pressure'], data['current']['humidity'])
    # Calculate power for forecast weather and add it to the data dict
    for forecast in data['forecast']:
        forecast['power'] = calculate_power(forecast['wind']['speed'], forecast['temp'], forecast['pressure'], forecast['humidity'])
    # Send data to Kafka
    send_to_kafka(data['city'], data)

def send_to_kafka(city, wind_data):
    try:
        # Send the data to the city topic
        producer.send(city.replace(" ", "_"), key=city.encode(), value=wind_data)
        producer.flush()
        # # For testing, send let's write the data to a file
        # with open('received.json', 'a') as file:
        #     file.write(json.dumps(wind_data, indent=4) + ",\n")
    except KafkaError:
        print("Failed to send data to Kafka")

if __name__ == "__main__":
    try:
        # Load environment variables
        bootstrap_servers = [os.getenv('KAFKA_BOOTSTRAP_SERVERS')]
        print("Starting consumer on " + bootstrap_servers[0] + "...")
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=json_serializer)
        consumer = KafkaConsumer('weather', bootstrap_servers=bootstrap_servers, value_deserializer=json_deserializer)
        print("Consumer started on topic 'weather', broker: " + bootstrap_servers[0])
        for message in consumer:
            Thread(target=process_data, args=(message.value,)).start()
    except KafkaError:
        print("Failed to connect to Kafka")





