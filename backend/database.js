const { MongoClient } = require('mongodb');
const config = require('./config');

const client = new MongoClient(config.mongodb.url, { useUnifiedTopology: true });

let dbInstance = null;

const connectDB = async () => {
  try {
    await client.connect();
    dbInstance = client.db(config.mongodb.dbName);
    console.log('Connected to MongoDB:', config.mongodb.url);
  } catch (error) {
    console.error('Could not connect to MongoDB:', error);
    process.exit(1);
  }
};

const getDB = () => {
  if (!dbInstance) {
    throw new Error('Must connect to MongoDB first');
  }
  return dbInstance;
};

module.exports = { connectDB, getDB };