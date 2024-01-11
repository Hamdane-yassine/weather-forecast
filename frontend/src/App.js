import React, { useState } from 'react';
import Navbar from './components/Navbar';
import WeatherInfo from './components/WeatherInfo';
import data from './data';
import DailyForecast from './components/DailyForecast';
import './style/App.css';

function App() {
  const [cityData, setCityData] = useState(null);
  const [dataa ,setDataa] = useState(data);
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
      <WeatherInfo currentData={dataa.current} forecastData={dataa.forecast} city={dataa.city} />
      <DailyForecast forecast={dataa.forecast}/>
    
    </>
    
  );
}

export default App;
