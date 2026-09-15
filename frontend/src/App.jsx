import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Books from "./pages/Books";
import ReadingTrends from "./pages/ReadingTrends";
import Readers from "./pages/Readers";
import Branches from "./pages/Branches";
import Collection from "./pages/Collection";
import DataQuality from "./pages/DataQuality";
import Reports from "./pages/Reports";

import "./App.css";

function App() {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const toggleSidebar = () => setSidebarOpen((prev) => !prev);
    const closeSidebar = () => setSidebarOpen(false);

    return (
        <BrowserRouter>
            <div className="app">
                <Navbar onToggleSidebar={toggleSidebar} />

                <div className="main-layout">
                    <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />

                    <main className="content">
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/dashboard" element={<Dashboard />} />
                            <Route path="/books" element={<Books />} />
                            <Route path="/readers" element={<Readers />} />
                            <Route path="/branches" element={<Branches />} />
                            <Route path="/reading-trends" element={<ReadingTrends />} />
                            <Route path="/collection" element={<Collection />} />
                            <Route path="/data-quality" element={<DataQuality />} />
                            <Route path="/reports" element={<Reports />} />
                            <Route path="*" element={<Navigate to="/" replace />} />
                        </Routes>
                    </main>
                </div>
            </div>
        </BrowserRouter>
    );
}

export default App;