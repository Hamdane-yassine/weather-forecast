import React from 'react';
import Navbar from './components/Navbar';

function App() {
  const handleCitySearch = async (city) => {
    try {
      // Make a GET request to the backend API
      const response = await fetch(`http://localhost:3001/search?city=${encodeURIComponent(city)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Data received:', data);
      // You can now set this data to state and pass it to other components if needed
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <div className="App">
      <Navbar onSearch={handleCitySearch} />
      {/* Other components will go here */}
    </div>
  );
}

export default App;
