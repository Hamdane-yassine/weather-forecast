require('dotenv').config();
const axios = require('axios');
const config = require('./config');

const getCityCoords = async (cityName) => {
  try {
    const response = await axios.get(config.geoApi.geoApiBaseUrl, {
      params: { 
        namePrefix: cityName,
        minPopulation: 100000,
        limit: 1 // Limit the results to 1 for direct access
      },
      headers: {
        'x-rapidapi-key': config.geoApi.rapidApiKey,
        'x-rapidapi-host': config.geoApi.rapidApiHost
      }
    });

    if (response.data && response.data.data && response.data.data.length > 0) {
      const cityInfo = response.data.data[0];
      return {
        latitude: cityInfo.latitude,
        longitude: cityInfo.longitude
      };
    }

    return null;
  } catch (error) {
    console.error('Error fetching city coordinates:', error);
    throw error; // handle as needed
  }
};

module.exports = getCityCoords;