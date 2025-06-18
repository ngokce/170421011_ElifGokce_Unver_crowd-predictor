import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navbar({ user, onLogout }) {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav style={{
      backgroundColor: '#22223b',
      padding: '1rem 2rem',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      position: 'sticky',
      top: 0,
      zIndex: 1000
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {/* Logo/Brand */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <Link 
            to="/home" 
            style={{
              fontSize: '1.5rem',
              fontWeight: 'bold',
              color: '#fff',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            🚗 CrowdPredictor
          </Link>
        </div>

        {/* Navigation Links */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '2rem'
        }}>
          <Link 
            to="/home" 
            style={{
              color: isActive('/home') ? '#fbbf24' : '#d1d5db',
              textDecoration: 'none',
              fontSize: '1rem',
              fontWeight: isActive('/home') ? '600' : '400',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              backgroundColor: isActive('/home') ? 'rgba(251, 191, 36, 0.1)' : 'transparent',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseOver={(e) => {
              if (!isActive('/home')) {
                e.target.style.color = '#fbbf24';
                e.target.style.backgroundColor = 'rgba(251, 191, 36, 0.1)';
              }
            }}
            onMouseOut={(e) => {
              if (!isActive('/home')) {
                e.target.style.color = '#d1d5db';
                e.target.style.backgroundColor = 'transparent';
              }
            }}
          >
            🏠 Ana Sayfa
          </Link>

          <Link 
            to="/history" 
            style={{
              color: isActive('/history') ? '#fbbf24' : '#d1d5db',
              textDecoration: 'none',
              fontSize: '1rem',
              fontWeight: isActive('/history') ? '600' : '400',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              backgroundColor: isActive('/history') ? 'rgba(251, 191, 36, 0.1)' : 'transparent',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseOver={(e) => {
              if (!isActive('/history')) {
                e.target.style.color = '#fbbf24';
                e.target.style.backgroundColor = 'rgba(251, 191, 36, 0.1)';
              }
            }}
            onMouseOut={(e) => {
              if (!isActive('/history')) {
                e.target.style.color = '#d1d5db';
                e.target.style.backgroundColor = 'transparent';
              }
            }}
          >
            📚 Geçmiş Aramalar
          </Link>

          <Link 
            to="/favorites" 
            style={{
              color: isActive('/favorites') ? '#fbbf24' : '#d1d5db',
              textDecoration: 'none',
              fontSize: '1rem',
              fontWeight: isActive('/favorites') ? '600' : '400',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              backgroundColor: isActive('/favorites') ? 'rgba(251, 191, 36, 0.1)' : 'transparent',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseOver={(e) => {
              if (!isActive('/favorites')) {
                e.target.style.color = '#fbbf24';
                e.target.style.backgroundColor = 'rgba(251, 191, 36, 0.1)';
              }
            }}
            onMouseOut={(e) => {
              if (!isActive('/favorites')) {
                e.target.style.color = '#d1d5db';
                e.target.style.backgroundColor = 'transparent';
              }
            }}
          >
            🌟 Favoriler
          </Link>
        </div>

        {/* User Info & Logout */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <div style={{
            color: '#d1d5db',
            fontSize: '0.875rem'
          }}>
            Hoş geldiniz, <strong style={{ color: '#fbbf24' }}>{user?.name}</strong>
          </div>
          <button
            onClick={onLogout}
            style={{
              backgroundColor: '#ef4444',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontSize: '0.875rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = '#dc2626';
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = '#ef4444';
            }}
          >
            🚪 Çıkış
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar; 