// utils/fetchData.js
import Papa from 'papaparse'; // Import papaparse for CSV parsing

// Fetch and extract data from a JSON file
export const fetchAndExtractJSON = async (filePath) => {
  try {
    const response = await fetch(filePath);
    const data = await response.json();

    return { rawData: data };
  } catch (error) {
    console.error(`Error fetching or processing data from ${filePath}:`, error);
    throw error; // Re-throw error for caller to handle
  }
};

// Fetch and extract data from a CSV file
export const fetchAndExtractCSV = async (filePath) => {
  try {
    const response = await fetch(filePath);
    const text = await response.text();

    // Parse CSV data using PapaParse
    const parsedData = Papa.parse(text, { header: true, skipEmptyLines: true });

    return { rawData: parsedData.data };
  } catch (error) {
    console.error(`Error fetching or processing CSV data from ${filePath}:`, error);
    throw error; // Re-throw error for caller to handle
  }
};
