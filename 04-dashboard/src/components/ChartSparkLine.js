// ChartSparkLine.js

import React from 'react';
import { SparkLineChart } from '@mui/x-charts/SparkLineChart';
import { Gauge } from '@mui/x-charts/Gauge';
import { processChartData } from '../utils/processChartData';
import GraphContainer from './GraphContainer';

const ChartSparkLine = ({ id, title, data, x, y = [], z = null, custom = null ,description = null }) => {
    const { values } = processChartData(data, x, y, z);

    return (
        <GraphContainer title={title} description={description}>
            {Object.entries(values).map(([key]) => (
                <div key={key} className="card card-chart" style={{ backgroundColor: '#f0f0f0' }}>
                    <h6>{key}</h6>
                    <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                        <div style={{ flexShrink: 0, width: '100px' }}> {/* Fixed width for the Gauge */}
                            <Gauge
                                value={parseFloat((values[key]?.at(-1) * 100).toFixed(2))}
                                startAngle={-110}
                                endAngle={110}
                                text={`${(values[key]?.at(-1) * 100).toFixed(2)}%`}
                                height={100}
                            />
                        </div>
                        <div style={{ flexGrow: 1 }}> {/* Take up the remaining space */}
                            <SparkLineChart
                                plotType="line"
                                data={values[key]}
                                height={100}
                            />
                        </div>
                    </div>
                </div>
            ))}
        </GraphContainer>
    );
};

export default ChartSparkLine;
