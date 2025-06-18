import React, { useState, useEffect } from 'react';

function FavoritesPage() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Lütfen giriş yapın');
        setLoading(false);
        return;
      }

      const response = await fetch('http://localhost:5050/favorites', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        setFavorites(data.favorites);
      } else {
        setError(data.message || 'Favoriler yüklenirken hata oluştu');
      }
    } catch (error) {
      setError('Sunucuya bağlanırken hata oluştu');
      console.error('Fetch favorites error:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeFavorite = async (favoriteId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5050/favorites/${favoriteId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setFavorites(favorites.filter(fav => fav.id !== favoriteId));
      } else {
        const data = await response.json();
        setError(data.message || 'Favori silinirken hata oluştu');
      }
    } catch (error) {
      setError('Sunucuya bağlanırken hata oluştu');
      console.error('Remove favorite error:', error);
    }
  };

  const predictTraffic = async (favorite) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5050/predict', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          origin: favorite.origin,
          destination: favorite.destination,
          datetime: new Date().toISOString()
        }),
      });

      const data = await response.json();

      if (response.ok) {
        alert(`Trafik Durumu: ${data.traffic_info.description}`);
      } else {
        setError(data.error || 'Trafik tahmini yapılırken hata oluştu');
      }
    } catch (error) {
      setError('Sunucuya bağlanırken hata oluştu');
      console.error('Predict traffic error:', error);
    }
  };

  if (loading) {
    return (
      <div style={{
        padding: '2rem',
        textAlign: 'center',
        color: '#6b7280'
      }}>
        Favoriler yükleniyor...
      </div>
    );
  }

  return (
    <div style={{
      padding: '2rem',
      maxWidth: '800px',
      margin: '0 auto',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{
        fontSize: '2rem',
        fontWeight: 'bold',
        color: '#22223b',
        marginBottom: '2rem',
        textAlign: 'center'
      }}>
        🌟 Favori Rotalarım
      </h1>

      {error && (
        <div style={{
          backgroundColor: '#fee2e2',
          color: '#dc2626',
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '1rem',
          textAlign: 'center'
        }}>
          {error}
        </div>
      )}

      {favorites.length === 0 ? (
        <div style={{
          textAlign: 'center',
          color: '#6b7280',
          fontSize: '1.1rem',
          padding: '3rem'
        }}>
          Henüz favori rotanız yok. Geçmiş aramalarınızdan rota ekleyebilirsiniz.
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gap: '1rem'
        }}>
          {favorites.map((favorite) => (
            <div key={favorite.id} style={{
              backgroundColor: '#f9fafb',
              border: '1px solid #e5e7eb',
              borderRadius: '12px',
              padding: '1.5rem',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
            }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: '1rem'
              }}>
                <div>
                  <h3 style={{
                    fontSize: '1.25rem',
                    fontWeight: '600',
                    color: '#22223b',
                    margin: '0 0 0.5rem 0'
                  }}>
                    {favorite.route_name || `${favorite.origin} - ${favorite.destination}`}
                  </h3>
                  <p style={{
                    color: '#6b7280',
                    margin: '0 0 0.25rem 0'
                  }}>
                    <strong>Başlangıç:</strong> {favorite.origin}
                  </p>
                  {favorite.destination && (
                    <p style={{
                      color: '#6b7280',
                      margin: '0 0 0.25rem 0'
                    }}>
                      <strong>Varış:</strong> {favorite.destination}
                    </p>
                  )}
                  <p style={{
                    color: '#9ca3af',
                    fontSize: '0.875rem',
                    margin: '0'
                  }}>
                    Ekleme Tarihi: {new Date(favorite.created_at).toLocaleDateString('tr-TR')}
                  </p>
                </div>
                <div style={{
                  display: 'flex',
                  gap: '0.5rem'
                }}>
                  <button
                    onClick={() => predictTraffic(favorite)}
                    style={{
                      backgroundColor: '#22223b',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseOver={(e) => {
                      e.target.style.backgroundColor = '#1a1a2e';
                    }}
                    onMouseOut={(e) => {
                      e.target.style.backgroundColor = '#22223b';
                    }}
                  >
                    🚦 Tahmin Et
                  </button>
                  <button
                    onClick={() => removeFavorite(favorite.id)}
                    style={{
                      backgroundColor: '#ef4444',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseOver={(e) => {
                      e.target.style.backgroundColor = '#dc2626';
                    }}
                    onMouseOut={(e) => {
                      e.target.style.backgroundColor = '#ef4444';
                    }}
                  >
                    🗑️ Sil
                  </button>
                </div>
              </div>

              <div style={{
                backgroundColor: '#e0f2fe',
                border: '1px solid #b3e5fc',
                borderRadius: '6px',
                padding: '0.75rem',
                fontSize: '0.875rem'
              }}>
                {favorite.search_datetime ? (
                  <>
                    <strong>Arama Tarihi:</strong> {new Date(favorite.search_datetime).toLocaleString('tr-TR')}
                    <br />
                    {favorite.prediction_result && (
                      <>
                        <strong>Son Tahmin:</strong> {JSON.parse(favorite.prediction_result)?.traffic_info?.description || 'Tahmin bilgisi mevcut değil'}
                      </>
                    )}
                  </>
                ) : (
                  <>
                    <strong>Durum:</strong> Manuel olarak eklenmiş favori rota
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FavoritesPage; 