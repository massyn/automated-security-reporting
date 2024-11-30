import React, { useEffect, useState } from 'react';

import ChartLine from '../components/ChartLine';
import Filters from '../components/Filters';

import { fetchAndExtractCSV } from '../utils/fetchData';
import { weightedCalculation } from '../utils/weightedCalculations';

import '../style.css';

const Overview = () => {
  const [rawData, setRawData] = useState(null);
  const [selected_filters, setSelected_filters] = useState('');
  const [chart1_filteredData, setChart1_filteredData] = useState(null);
  const [chart2_filteredData, setChart2_filteredData] = useState(null);

  // Download the raw data
  useEffect(() => {
    const initializeData = async () => {
      try {
        const data = await fetchAndExtractCSV('/summary.csv');
        setRawData(data.rawData);

        const chart1_aggregatedData = weightedCalculation(data.rawData);
        setChart1_filteredData(chart1_aggregatedData);

        const chart2_aggregatedData = weightedCalculation(data.rawData, {}, 'business_unit');
        setChart2_filteredData(chart2_aggregatedData);

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
      const chart1_aggregatedData = weightedCalculation(rawData, updatedFilters);
      setChart1_filteredData(chart1_aggregatedData);

      const chart2_aggregatedData = weightedCalculation(rawData, updatedFilters, 'business_unit');
      setChart2_filteredData(chart2_aggregatedData);
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
      <h1 className="my-4">Overview Page</h1>
      <p>The overview page provides an executive overview of how the organisation is performing.</p>
      <div className="row">
        <div className="col-md-3">
          <Filters
            data={rawData}
            onChange={handleDropdownChange}
            filters={selected_filters}
          />
        </div>

        <div className="col-md-9">
          <ChartLine
              id="orgCategories"
              title="Organisational score over time"
              description="Organisational performance across all metrics."
              data={chart1_filteredData}
              x="datestamp"
              y={[ "value" , "slo" , "slo_min"]}
              custom={ { "value" : { "label" : "Score", "showMark" : true } , "slo" : { "color" : "green", "label" : "Target"}, "slo_min" : { "color" : "yellow" , label: "SLO min"} }}
          />
          <ChartLine
              id="BUCategories"
              title="Business Unit score over time"
              description="View the scores for all business units in one multi-line graph."
              data={chart2_filteredData}
              x="datestamp"
              y={[ "value" ]}
              z="business_unit"
          />
        </div>
      </div>
    </div>
  );
};

export default Overview;
