import React, { useState } from 'react';
import { AsyncPaginate } from 'react-select-async-paginate'
import { getCitiesList } from '../geoApi';

function Navbar({ onSearch }) {
  const [cityPrefix, setCityPrefix] = useState('');

  const handleSearchChange = (e) => {
    setCityPrefix(e);
    onSearch(e);
  };

  const loadOptions = (cityPrefix) => {
    return getCitiesList(cityPrefix);
  };

  return (
    <nav>
      <AsyncPaginate
        placeholder="Enter city name"
        debounceTimeout={1000}
        value={cityPrefix}
        onChange={handleSearchChange}
        loadOptions={loadOptions}
      />
      
    </nav>
  );
}

export default Navbar;