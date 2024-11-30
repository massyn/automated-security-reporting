export const processChartData = (data, x, y, z) => {
    let data_clean;

    if (!z) {
        data_clean = data.map((item) =>
            [...new Set([x, ...y])].reduce((acc, key) => {
                if (key in item) {
                    acc[key] = item[key];
                }
                return acc;
            }, {})
        );
    } else {
        data_clean = data.reduce((acc, item) => {
            const existing = acc.find(record => record[x] === item[x]);
            if (existing) {
                existing[item[z]] = item[y[0]];
            } else {
                const newRecord = {
                    [x]: item[x],
                    [item[z]]: item[y[0]],
                };
                acc.push(newRecord);
            }
            return acc;
        }, []);
    }

    const fieldNames = data_clean.length > 0 
        ? Object.keys(data_clean[data_clean.length - 1]).filter(field => field !== x) 
        : [];

    // Sort labels and reorder values accordingly
    const sortedData = data_clean.sort((a, b) => 
        (a[x] > b[x] ? 1 : -1)
    );

    const labels = sortedData.map((item) => item[x]);

    const values = fieldNames.reduce((acc, field) => {
        acc[field] = sortedData.map((item) => {
            const value = item[field];
            return isNaN(value) || value === null ? 0 : value; // Replace NaN or null with 0
        });
        return acc;
    }, {});
    
    return { labels, values };
};