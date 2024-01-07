const express = require('express');
const cors = require('cors');
const { connectDB, getDB } = require('./database');
const app = express();
const port = 3001; // Use a different port from your React app

app.use(cors());

// Middleware to parse JSON bodies
app.use(express.json());

// Connect to MongoDB
connectDB().then(() => {
  console.log('Connected to MongoDB');
}).catch(error => {
  console.error('Database connection failed', error);
  process.exit(1);
});

// Test route
app.get('/', (req, res) => {
  res.send('Hello from the backend!');
});

// Route to handle city search
app.get('/search', async (req, res) => {
  try {
    const city = req.query.city; // Extract city from query parameters
    console.log('City received:', city);
    const db = getDB();

    // Query the database for the city data
    const cityData = await db.collection('cities').findOne({ name: city });
      if (cityData) {
        res.json(cityData);
      } else {
        res.status(404).send('City not found');
      }
    } catch (error) {
      console.log(error)
      res.status(500).send('Error accessing database');
    }
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
