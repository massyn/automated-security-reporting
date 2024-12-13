import React, { useState, useEffect } from "react";
import Menu from "./components/Menu";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Overview from "./pages/overview";
import Metrics from "./pages/metrics";
import MetricPage from './pages/metricpage';
import Help from "./pages/help";

function App() {
    const [darkMode, setDarkMode] = useState(() => {
        // Set darkMode to true by default, or load it from localStorage
        return JSON.parse(localStorage.getItem("darkMode")) || true;
    });

    // Apply dark mode class to the body
    useEffect(() => {
        document.body.classList.toggle("dark-mode", darkMode);
        localStorage.setItem("darkMode", JSON.stringify(darkMode)); // Save state to localStorage
    }, [darkMode]);

    return (
        <Router>
            <Menu darkMode={darkMode} setDarkMode={setDarkMode} />
            <div className="page-content">
                <Routes>
                    <Route exact path="/" element={<Overview />} />
                    <Route path="/metrics" element={<Metrics />} />
                    <Route path="/help" element={<Help />} />
                    <Route path="/metric/:id" element={<MetricPage />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
