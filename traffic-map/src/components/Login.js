// components/Login.js
import React, { useState } from "react";

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    
    if (!email || !password) {
      setError("Lütfen e-posta ve şifre girin.");
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:5050/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      console.log('Login response:', response.status, data);

      if (response.ok) {
        // Token'i localStorage'a kaydet
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        console.log('Login successful, calling onLogin with:', data.user);
        // Kullanıcıyı ana sayfaya yönlendir
        onLogin(data.user);
      } else {
        setError(data.message || 'Giriş yapılırken bir hata oluştu');
      }
    } catch (error) {
      setError('Sunucuya bağlanırken bir hata oluştu');
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{
      display: "flex",
      flexDirection: "column",
      gap: "1.5rem",
      width: "100%",
      maxWidth: "100%",
      boxSizing: "border-box"
    }}>
      <h2 style={{
        fontSize: "1.75rem",
        fontWeight: "600",
        color: "#22223b",
        marginBottom: "0.5rem",
        textAlign: "center"
      }}>Hoş Geldiniz</h2>
      
      {error && (
        <div style={{
          backgroundColor: "#fee2e2",
          color: "#dc2626",
          padding: "0.75rem",
          borderRadius: "8px",
          fontSize: "0.875rem",
          textAlign: "center",
          border: "1px solid #fecaca"
        }}>
          {error}
        </div>
      )}
      
      <div style={{ 
        position: "relative",
        width: "100%",
        boxSizing: "border-box"
      }}>
        <input
          type="email"
          placeholder="E-posta"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{
            width: "100%",
            padding: "0.75rem 1rem",
            borderRadius: "8px",
            border: "1px solid #e5e7eb",
            fontSize: "1rem",
            transition: "all 0.3s ease",
            outline: "none",
            backgroundColor: "#f9fafb",
            color: "#22223b",
            boxSizing: "border-box"
          }}
          onFocus={(e) => {
            e.target.style.borderColor = "#22223b";
            e.target.style.boxShadow = "0 0 0 2px rgba(34, 34, 59, 0.1)";
          }}
          onBlur={(e) => {
            e.target.style.borderColor = "#e5e7eb";
            e.target.style.boxShadow = "none";
          }}
        />
      </div>

      <div style={{ 
        position: "relative",
        width: "100%",
        boxSizing: "border-box"
      }}>
        <input
          type="password"
          placeholder="Şifre"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{
            width: "100%",
            padding: "0.75rem 1rem",
            borderRadius: "8px",
            border: "1px solid #e5e7eb",
            fontSize: "1rem",
            transition: "all 0.3s ease",
            outline: "none",
            backgroundColor: "#f9fafb",
            color: "#22223b",
            boxSizing: "border-box"
          }}
          onFocus={(e) => {
            e.target.style.borderColor = "#22223b";
            e.target.style.boxShadow = "0 0 0 2px rgba(34, 34, 59, 0.1)";
          }}
          onBlur={(e) => {
            e.target.style.borderColor = "#e5e7eb";
            e.target.style.boxShadow = "none";
          }}
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        style={{
          backgroundColor: loading ? "#9ca3af" : "#fff",
          color: loading ? "#fff" : "#22223b",
          padding: "0.75rem 1.5rem",
          borderRadius: "8px",
          border: "1px solid #22223b",
          fontSize: "1rem",
          fontWeight: "500",
          cursor: loading ? "not-allowed" : "pointer",
          transition: "all 0.3s ease",
          marginTop: "1rem",
          width: "100%",
          boxSizing: "border-box"
        }}
        onMouseOver={(e) => {
          if (!loading) {
            e.target.style.backgroundColor = "#22223b";
            e.target.style.color = "#fff";
          }
        }}
        onMouseOut={(e) => {
          if (!loading) {
            e.target.style.backgroundColor = "#fff";
            e.target.style.color = "#22223b";
          }
        }}
      >
        {loading ? "Giriş Yapılıyor..." : "Giriş Yap"}
      </button>

      <div style={{
        textAlign: "center",
        marginTop: "1rem",
        fontSize: "0.875rem",
        color: "#6b7280"
      }}>
        <a href="#" style={{
          color: "#22223b",
          textDecoration: "none",
          fontWeight: "500"
        }}>
          Şifremi Unuttum
        </a>
      </div>
    </form>
  );
}

export default Login;