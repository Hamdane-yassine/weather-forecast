require('dotenv').config();

const config = {
  mongodb: {
    url: process.env.MONGODB_URL,
    dbName: process.env.MONGODB_DB_NAME
  },
  geoApi: {
    rapidApiKey: process.env.RAPIDAPI_KEY,
    geoApiBaseUrl: process.env.GEOAPI_BASE_URL,
    rapidApiHost: 'wft-geo-db.p.rapidapi.com'
  },
  server: {
    host: process.env.HOST || 'localhost',
    port: process.env.PORT || 3001
  }
};

module.exports = config;