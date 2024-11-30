// GraphContainer.js

import React from 'react';

const GraphContainer = ({ title, description, children }) => {
    return (
        <div className="card card-chart">
            <h5 className="card-title">{title}</h5>
            <p>{description}</p>
            {children}
        </div>
    );
};

export default GraphContainer;