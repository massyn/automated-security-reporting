import React, { useRef, useEffect } from 'react';
import Chart from 'chart.js/auto';
import { processChartData } from '../utils/processChartData';
import GraphContainer from '../components/GraphContainer';

const ComboTrend = ({ id, title, data, x, y = [], z = null, custom = null, description = null }) => {
    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    useEffect(() => {
        const { labels, values } = processChartData(data, x, y, z);
        const datasets = Object.entries(values).map(([key], index) => ({
            label: custom?.[key]?.label ?? key,
            data: values[key].map((value) => (value * 100).toFixed(2)),
            type: custom?.[key]?.type ?? 'line',
            backgroundColor: custom?.[key]?.color ?? [
                'blue', 'green', 'red', 'yellow', 'purple',
                'brown', 'black', 'orange', 'pink', 'cyan', 'magenta', 'white', 'gray'
            ][index % 13],
            borderColor: custom?.[key]?.color ?? [
                'blue', 'green', 'red', 'yellow', 'purple',
                'brown', 'black', 'orange', 'pink', 'cyan', 'magenta', 'white', 'gray'
            ][index % 13],
            fill: false,
            tension: 0.1,
        }));

        if (chartInstance.current) {
            chartInstance.current.destroy();
        }

        chartInstance.current = new Chart(chartRef.current, {
            type: 'line',
            data: {
                labels,
                datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.dataset.label}: ${context.raw}%`,
                        },
                    },
                },
                scales: {
                    x: {
                        type: 'category',
                        title: {
                            display: false
                        },
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: false
                        },
                        ticks: {
                            callback: (value) => `${value}%`,
                        },
                    },
                },
            },
        });

        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [data, x, y, z, custom]);

    return (
        <GraphContainer title={title} description={description}>
            <div style={{ width: '800px', height: '400px' }}>
                <canvas ref={chartRef} />
            </div>
        </GraphContainer>
    );
};

export default ComboTrend;
