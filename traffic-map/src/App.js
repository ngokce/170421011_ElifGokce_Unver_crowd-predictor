// App.js
import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import HomePage from "./pages/HomePage";
import FavoritesPage from "./pages/FavoritesPage";
import SearchHistoryPage from "./pages/SearchHistoryPage";
import Navbar from "./components/Navbar";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Sayfa yüklendiğinde token kontrolü yap
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
        setIsAuthenticated(true);
      } catch (error) {
        // Bozuk JSON temizle
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#f9fafb'
      }}>
        <div style={{
          fontSize: '1.5rem',
          color: '#6b7280'
        }}>
          Yükleniyor...
        </div>
      </div>
    );
  }

  return (
    <Router>
      {isAuthenticated && <Navbar user={user} onLogout={handleLogout} />}
      <Routes>
        <Route 
          path="/" 
          element={
            isAuthenticated ? 
            <Navigate to="/home" replace /> : 
            <LoginPage onLogin={handleLogin} />
          } 
        />
        <Route 
          path="/home" 
          element={
            isAuthenticated ? 
            <HomePage user={user} /> : 
            <Navigate to="/" replace />
          } 
        />
        <Route 
          path="/favorites" 
          element={
            isAuthenticated ? 
            <FavoritesPage /> : 
            <Navigate to="/" replace />
          } 
        />
        <Route 
          path="/history" 
          element={
            isAuthenticated ? 
            <SearchHistoryPage /> : 
            <Navigate to="/" replace />
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;