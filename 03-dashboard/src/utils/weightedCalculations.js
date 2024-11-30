
export const weightedCalculation = (data, filters = {}, dimension = null) => {
    // Apply the filter first
    const filteredData = data.filter(item =>
        Object.entries(filters).every(([key, value]) => value === null || item[key] === value)
    );

    // Layer 1 - Aggregate the totals for each of the metrics
    const layer1 = {};
    filteredData.forEach(item => {
        const datestamp = item.datestamp;
        const itemDimension = item[dimension] || "None";
        const metricId = item.metric_id;

        if (!layer1[datestamp]) {
            layer1[datestamp] = {};
        }
        if (!layer1[datestamp][itemDimension]) {
            layer1[datestamp][itemDimension] = {};
        }
        if (!layer1[datestamp][itemDimension][metricId]) {
            layer1[datestamp][itemDimension][metricId] = {
                total: 0,
                totalok: 0,
                weight: 0,
                slo: 0,
                slo_min: 0
            };
        }

        const metric = layer1[datestamp][itemDimension][metricId];
        metric.total += parseFloat(item.total);
        metric.totalok += parseFloat(item.totalok);
        metric.weight = parseFloat(item.weight);
        metric.slo = parseFloat(item.slo);
        metric.slo_min = parseFloat(item.slo_min);
    });

    // Layer 2 - Aggregate dimensions
    const layer2 = {};
    Object.entries(layer1).forEach(([datestamp, dimensions]) => {
        layer2[datestamp] = {};
        Object.entries(dimensions).forEach(([itemDimension, metrics]) => {
            let weightSum = 0.0;
            let scoreSum = 0.0;

            Object.values(metrics).forEach(metric => {
                const score = metric.totalok / metric.total;
                weightSum += metric.weight;
                scoreSum += score * metric.weight;
            });

            layer2[datestamp][itemDimension] = {
                value: weightSum > 0 ? scoreSum / weightSum : 0,
                slo: metrics[Object.keys(metrics)[0]].slo,
                slo_min: metrics[Object.keys(metrics)[0]].slo_min
            };
        });
    });

    // Create result from Layer 2
    const result = [];
    Object.entries(layer2).forEach(([datestamp, dimensions]) => {
        Object.entries(dimensions).forEach(([itemDimension, data]) => {
            const resultItem = {
                datestamp: datestamp,
                value: data.value,
                slo: data.slo,
                slo_min: data.slo_min
            };

            // Include dimension only if it's not null
            if (dimension !== null) {
                resultItem[dimension] = itemDimension;
            }

            result.push(resultItem);
        });
    });

    return result;
};