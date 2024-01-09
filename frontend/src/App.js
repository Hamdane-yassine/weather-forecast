import React, { useState } from 'react';
import config from './config';
import Navbar from './components/Navbar';
import CityData from './components/CityData';

function App() {
  const [cityData, setCityData] = useState(null);

  const handleCitySearch = async (city) => {
    try {
      // Make a GET request to the backend API
      const response = await fetch(`${config.backendUrl}/search?city=${encodeURIComponent(city)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Data received:', data);
      // You can now set this data to state and pass it to other components if needed
      setCityData(data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setCityData(null);
    }
  };

  return (
    <div className="App">
      <Navbar onSearch={handleCitySearch} />
      <CityData cityData={cityData} />
      {/* Other components will go here */}
    </div>
  );
}

export default App;
