import React from 'react';

function CityData({ cityData }) {
  if (!cityData) {
    return <div>No data to display</div>;
  }

  return (
    <div>
      <h2>{cityData.name}</h2>
      <p>{cityData.data}</p>
      {/* Render additional city data here */}
    </div>
  );
}

export default CityData;