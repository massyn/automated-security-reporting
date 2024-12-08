import React, { useEffect, useState } from 'react';
import { fetchAndExtractCSV } from '../utils/fetchData';
import Filters from '../components/Filters';
import ChartSparkLine from '../components/ChartSparkLine';
import { weightedCalculation } from '../utils/weightedCalculations';
import '../style.css';

const Categories = () => {
  const [rawData, setRawData] = useState(null);
  const [selected_filters, setSelected_filters] = useState('');
  const [chart1_filteredData, setChart1_filteredData] = useState(null);

  // Download the raw data
  useEffect(() => {
    const initializeData = async () => {
      try {
        const data = await fetchAndExtractCSV('/summary.csv');
        setRawData(data.rawData);

        const chart1_aggregatedData = weightedCalculation(data.rawData, {}, 'category');
        setChart1_filteredData(chart1_aggregatedData);

      } catch (error) {
        console.error('Error initializing data:', error);
      }
    };
    initializeData();
  }, []);

  // handle the dropdown
  const handleDropdownChange = (event) => {
    const { name, value } = event.target;
    const updatedFilters = {
      ...selected_filters,
      [name]: value,
    };
    setSelected_filters(updatedFilters);

    if (rawData) {
      const chart1_aggregatedData = weightedCalculation(rawData, updatedFilters, 'category');
      setChart1_filteredData(chart1_aggregatedData);
    }
  };

  // render the html
  if (!chart1_filteredData || !rawData) {
    return (
      <div className="spinner-container">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <h3 className="mt-3 text-dark">Please wait while the data is loading...</h3>
          <p className="text-muted">This may take a moment depending on the size of your data.</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container">
      <h1 className="my-4">Categories</h1>
      <p>On this page, metrics are aggregated to their defined categories.</p>
      <div className="row">
        <div className="col-md-3">
        <Filters
            data={rawData}
            onChange={handleDropdownChange}
            filters={selected_filters}
          />
        </div>

        <div className="col-md-9">
          <ChartSparkLine
              id="CATCategories"
              title="Categories"
              description="A breakdown of each of the categories with their individual scores"
              data={chart1_filteredData}
              x="datestamp"
              y={[ "value" ]}
              z="category"
          />
        </div>
      </div>
    </div>
  );
};

export default Categories;
