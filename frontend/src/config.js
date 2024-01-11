const config = {
    backendUrl: process.env.REACT_APP_BACKEND_URL || 'http://localhost:3001',
    geoApi: {
        rapidApiKey: process.env.REACT_APP_RAPIDAPI_KEY,
        geoApiBaseUrl: process.env.REACT_APP_GEOAPI_BASE_URL,
        rapidApiHost: 'wft-geo-db.p.rapidapi.com'
    }
};
export default config;