require('dotenv').config();

const config = {
  mongodb: {
    url: process.env.MONGODB_URL,
    dbName: process.env.MONGODB_DB_NAME
  },
  server: {
    host: process.env.HOST || 'localhost',
    port: process.env.PORT || 3001
  },
  kafka: {
    kafkaBootstrapServers: process.env.KAFKA_BOOTSTRAP_SERVERS
  }
};

module.exports = config;