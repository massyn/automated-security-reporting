import React, { useEffect, useState } from 'react';
import Filters from '../components/Filters';
import { fetchAndExtractCSV } from '../utils/fetchData';
import { useParams } from 'react-router-dom';
import { weightedCalculation } from '../utils/weightedCalculations';
import '../style.css';
import ComboTrend from '../components/ComboTrend';

const MetricPage = () => {
    const [rawData, setRawData] = useState(null);
    // Access the 'id' parameter from the URL
    const { id } = useParams();
    const [selected_filters, setSelected_filters] = useState('');
    const [chart1_filteredData, setChart1_filteredData] = useState(null);

    // Download the raw data
    useEffect(() => {
        const initializeData = async () => {
            try {
                const data = await fetchAndExtractCSV('/summary.csv');
                setRawData(data.rawData);

                const chart1_aggregatedData = weightedCalculation(data.rawData, { 'metric_id' : id }, 'category');
                setChart1_filteredData(chart1_aggregatedData);

            } catch (error) {
                console.error('Error initializing data:', error);
            }
        };
        initializeData();
    }, [id]);

    // handle the dropdown
    const handleDropdownChange = (event) => {
        const { name, value } = event.target;
        const updatedFilters = {
            ...selected_filters,
            [name]: value,
        };
        setSelected_filters(updatedFilters);

        if (rawData) {
            updatedFilters['metric_id'] = id;
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
        <h1 className="my-4">Metric Details - {id}</h1>
        <p>Viewing the details of a specific metric.</p>
        <div className="row">
            <div className="col-md-3">
                <Filters
                    data={rawData}
                    onChange={handleDropdownChange}
                    filters={selected_filters}
                />
            </div>

            <div className="col-md-9">
                <ComboTrend
                id="orgCategories"
                title={id}
                description="Metric score"
                data={chart1_filteredData}
                x="datestamp"
                y={[ "value" , "slo" , "slo_min"]}
                custom={ { "value" : { "label" : "Score", "showMark" : true } , "slo" : { "color" : "green", "label" : "Target"}, "slo_min" : { "color" : "yellow" , label: "SLO min"} }}
            />
            </div>
        </div>
    </div>
  );
}

export default MetricPage;
