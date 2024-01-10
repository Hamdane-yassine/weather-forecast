import axios from 'axios';
import config from './config';

export const getCitiesList = async (cityPrefix) => {
  try {
    const response = await axios.get(config.geoApi.geoApiBaseUrl, {
      params: { 
        namePrefix: cityPrefix,
        minPopulation: 1000000
      },
      headers: {
        'x-rapidapi-key': config.geoApi.rapidApiKey,
        'x-rapidapi-host': config.geoApi.rapidApiHost
      }
    });

    if (response.data && response.data.data && response.data.data.length > 0) {
      return {
        options: response.data.data.map((city) => {
          return {
            value: `${city.name};${city.latitude};${city.longitude}`,
            label: `${city.name}, ${city.countryCode}`,
          };
        }),
      };
    }

    return null;
  } catch (error) {
    console.error('Error fetching city coordinates:', error);
    throw error; // handle as needed
  }
};
