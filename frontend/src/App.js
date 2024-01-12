import React, { useState } from 'react';
import Navbar from './components/Navbar';
import WeatherInfo from './components/WeatherInfo';
import DailyForecast from './components/DailyForecast';
import './style/App.css';

function App() {
  const [cityData, setCityData] = useState(null);
  
  const handleCitySearch = async (e) => {
    const [city, lat, lon] = e.value.split(";");
    try {
      // Make a GET request to the backend API
      const response = await fetch(`/search?city=${encodeURIComponent(city)}&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`);
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
    <>  
      <div className="container">
      <Navbar onSearch={handleCitySearch} />
      </div>
      {cityData ? <WeatherInfo currentData={cityData.current} forecastData={cityData.forecast} city={cityData.city} /> : <p></p>}
      {cityData ? <DailyForecast forecast={cityData.forecast}/> : <p></p>}
      
      
    
    </>
    
  );
}

export default App;


// Test CI pipeline

