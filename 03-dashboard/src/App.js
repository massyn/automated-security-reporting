import React from "react";
import Menu from "./components/Menu";
import {
    BrowserRouter as Router,
    Routes,
    Route,
} from "react-router-dom";
import Overview from "./pages/overview";
import Metrics from "./pages/metrics"
import Categories from "./pages/categories"
import Help from "./pages/help"

function App() {
    return (
        <Router>
            <Menu />
            <Routes>
                <Route exact path="/" element={<Overview />} />
                <Route path="/categories" element={<Categories />} />
                <Route path="/metrics" element={<Metrics />} />
                <Route path="/help" element={<Help />} />
            </Routes>
        </Router>
    );
}

export default App;
