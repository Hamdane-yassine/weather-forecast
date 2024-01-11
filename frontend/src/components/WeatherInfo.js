// WeatherInfo.js
import React from 'react';
import '../style/WeatherInfo.css';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const WeatherInfo = ({ city,currentData, forecastData }) => {
  const renderHistogram = () => {
    // Mettez en œuvre la logique pour afficher l'histogramme en fonction de forecastData
    if (!forecastData || forecastData.length === 0) {
      return null;
    }

    const data = forecastData.map((forecastItem, index) => ({
    day: new Date(forecastItem.date).toLocaleDateString('en-US', { weekday: 'long' }),
    power: forecastItem.total_power || 0,
  }));

    return (
      <BarChart width={550} height={200} data={data} margin={{ top: 30, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="day" />
        <YAxis label={{ value: 'Power (W)', angle: 0, position: 'top' ,offset:18}} />
        <Tooltip />
        <Legend />
        <Bar dataKey="power" fill="#8884d8" />
      </BarChart>
    );
  };

  return (
    <div className="weather-info">
      <div className="real-time-card">
        <h2>{city}</h2>
        <div className="Adapt">
        <p>Temperature: {currentData.temp}°C</p>
        <p>Pressure: {(currentData.pressure / 100000).toFixed(2)} bar</p>
        <p>Humidity: {Math.ceil(currentData.humidity * 100)}%</p>
        <p>Wind Speed: {currentData.wind.speed} m/s</p>
        <p>Wind Direction: {currentData.wind.deg}°</p>
        </div>
      </div>
      <div className="forecast-chart-card">
        <h2>Forecast Power Chart</h2>
        {renderHistogram()}
      </div>
    </div>
  );
};

export default WeatherInfo;
