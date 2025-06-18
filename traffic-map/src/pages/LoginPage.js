// LoginPage.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Login from "../components/Login";
import Register from "../components/Register";
import "../App.css";
import trafficBg from "../assets/traffic-bg.jpg";

function LoginPage({ onLogin }) {
  const [showLogin, setShowLogin] = useState(true);
  const navigate = useNavigate();

  const handleLogin = (userData) => {
    // Login component'den gelen userData'yı App.js'e ilet
    if (onLogin) {
      onLogin(userData);
    }
    navigate("/home");
  };

  const handleRegisterSuccess = () => {
    // Kayıt başarılı olunca login sekmesine geç
    setShowLogin(true);
  };

  return (
    <div
      className="login-page"
      style={{
        minHeight: "100vh",
        background: `linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)), url(${trafficBg}) no-repeat center center fixed`,
        backgroundSize: "cover",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
      }}
    >
      <div 
        className="auth-container"
        style={{
          backgroundColor: "rgba(255, 255, 255, 0.95)",
          borderRadius: "15px",
          padding: "2rem",
          width: "100%",
          maxWidth: "400px",
          boxShadow: "0 8px 32px rgba(0, 0, 0, 0.2)",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255, 255, 255, 0.2)"
        }}
      >
        <div 
          className="tab-buttons"
          style={{
            display: "flex",
            marginBottom: "2rem",
            borderBottom: "2px solid #eee",
            paddingBottom: "0.5rem"
          }}
        >
          <button
            className={`tab-btn${showLogin ? " active" : ""}`}
            onClick={() => setShowLogin(true)}
            style={{
              flex: 1,
              padding: "0.75rem",
              border: "none",
              background: "none",
              fontSize: "1.1rem",
              fontWeight: showLogin ? "600" : "400",
              color: showLogin ? "#4B0082" : "#666",
              cursor: "pointer",
              transition: "all 0.3s ease",
              borderBottom: showLogin ? "2px solid #4B0082" : "none",
              marginBottom: "-2px"
            }}
          >
            Giriş Yap
          </button>
          <button
            className={`tab-btn${!showLogin ? " active" : ""}`}
            onClick={() => setShowLogin(false)}
            style={{
              flex: 1,
              padding: "0.75rem",
              border: "none",
              background: "none",
              fontSize: "1.1rem",
              fontWeight: !showLogin ? "600" : "400",
              color: !showLogin ? "#4B0082" : "#666",
              cursor: "pointer",
              transition: "all 0.3s ease",
              borderBottom: !showLogin ? "2px solid #4B0082" : "none",
              marginBottom: "-2px"
            }}
          >
            Kayıt Ol
          </button>
        </div>
        {showLogin ? <Login onLogin={handleLogin} /> : <Register onRegisterSuccess={handleRegisterSuccess} />}
      </div>
    </div>
  );
}

export default LoginPage;