import React from 'react';
import Navbar from './components/Navbar';

function App() {
  const handleCitySearch = (city) => {
    console.log('Searching for:', city);
    // Later, this will make a request to your backend
  };

  return (
    <div className="App">
      <Navbar onSearch={handleCitySearch} />
      {/* Other components will go here */}
    </div>
  );
}

export default App;
