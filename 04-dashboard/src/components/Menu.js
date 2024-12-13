import React from "react";
import { Navbar, Nav, Container } from "react-bootstrap";
import { FaSun, FaMoon } from "react-icons/fa"; // Import icons

const Menu = ({ darkMode, setDarkMode }) => {
    return (
        <Navbar bg={darkMode ? "dark" : "primary"} variant={darkMode ? "dark" : "dark"}>
            <Container>
                <Navbar.Brand href="/">Automated Security Reporting</Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <Nav.Link href="/">Overview</Nav.Link>
                        <Nav.Link href="/metrics">Metrics</Nav.Link>
                        <Nav.Link href="/help">Help</Nav.Link>
                    </Nav>
                    {/* Dark mode toggle button inside the navbar */}
                    <button
                        className={`button-toggle ${darkMode ? "dark-mode" : "dark-mode"}`}
                        onClick={() => setDarkMode(!darkMode)}
                    >
                        {darkMode ? <FaSun /> : <FaMoon />}
                    </button>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Menu;
