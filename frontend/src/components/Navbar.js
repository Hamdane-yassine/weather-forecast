import React, { useState } from 'react';

function Navbar({ onSearch }) {
  const [city, setCity] = useState('');

  const handleSearchChange = (e) => {
    setCity(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(city);
  };

  return (
    <nav>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          placeholder="Enter city name" 
          value={city} 
          onChange={handleSearchChange} 
        />
        <button type="submit">Search</button>
      </form>
    </nav>
  );
}

export default Navbar;