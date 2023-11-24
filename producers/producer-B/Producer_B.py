import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

class OpenMeteoDataFetcher:
    def __init__(self, latitude, longitude, start_date, end_date, variables):
        self.latitude = latitude
        self.longitude = longitude
        self.start_date = start_date
        self.end_date = end_date
        self.variables = variables

        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)

    def fetch_weather_data(self):
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "hourly": self.variables
        }
        responses = self.openmeteo.weather_api(url, params=params)
        return responses

    def process_weather_data(self, response):
        print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s"),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }

        for i, variable in enumerate(self.variables):
            values = hourly.Variables(i).ValuesAsNumpy()
            hourly_data[variable] = values

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        return hourly_dataframe

def fetch_weather_for_cities(file_path, start_date, end_date, variables):
    # Load CSV file into a pandas DataFrame
    df = pd.read_csv(file_path, header=None, names=["latitude", "longitude", "city", "country", "region"])

    for index, row in df.iterrows():
        print(f"\nFetching weather data for {row['city']}, {row['country']}")
        fetcher = OpenMeteoDataFetcher(row['latitude'], row['longitude'], start_date, end_date, variables)
        responses = fetcher.fetch_weather_data()
        for response in responses:
            hourly_dataframe = fetcher.process_weather_data(response)
            print(hourly_dataframe)

if __name__ == "__main__":
    file_path = "test.csv"  
    start_date = "2022-01-05"
    end_date = "2022-01-06"
    selected_variables = ["temperature_2m", "precipitation"]

    fetch_weather_for_cities(file_path, start_date, end_date, selected_variables)
