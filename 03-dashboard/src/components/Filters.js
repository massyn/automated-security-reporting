import React from 'react';

const FilterDropdown = ({ label, chartData, value, onChange, name }) => {
  // Dynamically derive the unique values for the dropdown
  const uniqueValues = [...new Set(chartData.map((item) => item[name]))];

  return (
    <div style={{ marginBottom: '20px', width: '100%' }}>
      <label htmlFor={`${name}-filter`} style={{ display: 'block', marginBottom: '8px' }}>
        {label}
      </label>
      <select
        id={`${name}-filter`}
        name={name}
        value={value}
        onChange={onChange}
        style={{
          width: '100%',
          padding: '8px',
          fontSize: '16px',
          borderRadius: '4px',
          border: '1px solid #ccc',
        }}
      >
        <option value="">All</option>
        {uniqueValues.map((option, index) => (
          <option key={index} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
};

const Filters = ({ data, filters, onChange }) => {

    return (
        <div className="card card-filters">
            <h5 className="card-title">Filters</h5>
            <FilterDropdown
              label="Business Unit"
              chartData={data}
              value={filters.business_unit}
              onChange={onChange}
              name="business_unit"
            />
            <FilterDropdown
              label="Team"
              chartData={data}
              value={filters.team}
              onChange={onChange}
              name="team"
            />
            <FilterDropdown
              label="Location"
              chartData={data}
              value={filters.location}
              onChange={onChange}
              name="location"
            />
        </div>
    );
}

export default Filters;