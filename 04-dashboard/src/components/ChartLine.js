// Charts.js

import React from 'react';
import { LineChart } from '@mui/x-charts/LineChart';
import { processChartData } from '../utils/processChartData'
import GraphContainer from '../components/GraphContainer'

const ChartLine = ({ id, title, data, x, y = [], z = null, custom = null ,description = null } ) => {
    const { labels, values } = processChartData(data, x, y, z);
    return (
        <GraphContainer title={title} description={description}>
            <LineChart
                xAxis={[{
                    id: id,
                    data: labels,
                    scaleType: 'band',
                }]}
                yAxis={[{
                    id: 'percentageAxis',
                    min: 0,
                    max: 100,
                    valueFormatter: (value) => `${value}%`,
                }]}
                series={Object.entries(values).map(([key], index) => ({
                    id: key,
                    data: values[key].map((value) => (value * 100).toFixed(2)),
                    label: custom?.[key]?.label ?? key,
                    color: custom?.[key]?.color ?? ['blue', 'green', 'red', 'yellow', 'purple', 'brown', 'black', 'orange', 'pink', 'cyan', 'magenta', 'white', 'gray'][index % 13],
                    showMark: custom?.[key]?.showMark ?? false,
                }))}
                width={800}
                height={400}
            />
        </GraphContainer>
    );
};

export default ChartLine;
