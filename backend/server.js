const express = require('express');
const cors = require('cors');
const app = express();
const port = 3001; // Use a different port from your React app

app.use(cors());

// Middleware to parse JSON bodies
app.use(express.json());

// Test route
app.get('/', (req, res) => {
  res.send('Hello from the backend!');
});

// Route to handle city search
app.get('/search', (req, res) => {
  const city = req.query.city; // Extract city from query parameters
  console.log('City received:', city);
  // Placeholder for database search logic
  res.json({ message: `Searching for ${city}` });
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
