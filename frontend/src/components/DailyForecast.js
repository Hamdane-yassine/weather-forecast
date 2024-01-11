import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import data from '../data'; // Assurez-vous d'utiliser le bon chemin d'accès à votre fichier JSON
import '../style/DailyForecast.css'; // Assurez-vous que le chemin d'importation est correct
import '../style/WeatherInfo.css';

const DailyForecast = ({ forecast }) => {
  const renderLineChart = (powerDetails) => {
    // Assurez-vous que les données de puissance contiennent l'heure et la puissance
    const formattedData = powerDetails.map(detail => ({
      hour: detail.time, // ou detail.dt si vous utilisez cette clé
      power: detail.power
    }));

    return (
      <LineChart width={300} height={200} data={formattedData} >
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey="hour" />
        <YAxis label={{ value: 'Power (W)', angle: 0, position: 'right' ,dx:2, dy:-70 }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="power" stroke="#8884d8" dot={false} />
      </LineChart>
    );
  };

  return (
    <div className="daily-forecast">

      {forecast.map((day, index) => (
        <div key={index} className="weather-info-f">
          <div className="real-time-card">
            {/* Affichez ici les détails météorologiques de la journée */}
            <h3>{`${new Date(day.date).toLocaleDateString('en-US', { weekday: 'long' })}`}</h3>
            <p>Temperature: {day.temp}°C</p>
            <p>Pressure: {(day.pressure / 100000).toFixed(2)} bar</p>
            <p>Humidity: {Math.ceil(day.humidity * 100)}%</p>
            <p>Wind Speed: {day.wind.speed} m/s</p>
            <p>Wind Direction: {day.wind.deg}°</p>
            <p>Wind gust: {day.wind.deg} m/s</p>
          </div>
          <div className="forecast-chart-card">
            <h3>{`Daily power evolution`}</h3>
            {renderLineChart(day.power_detail)}
          </div>
        </div>
      ))}
    </div>
  );
};

export default DailyForecast;
