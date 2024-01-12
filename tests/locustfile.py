from locust import HttpUser, task, between
import csv
import random

class UserBehavior(HttpUser):
    wait_time = between(1, 5)  # Time between tasks, can be adjusted for frequency

    def on_start(self):
        """ Read the CSV file and store the data """
        self.cities = []
        with open('./worldcities.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.cities.append(row)

    @task
    def send_request(self):
        """ Send a request to the backend for a random city """
        city = random.choice(self.cities)
        self.client.get(f"/search?city={city['city_ascii']}&lat={city['lat']}&lon={city['lng']}")