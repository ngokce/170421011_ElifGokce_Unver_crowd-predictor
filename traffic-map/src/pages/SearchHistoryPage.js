import React, { useState, useEffect } from 'react';

function SearchHistoryPage() {
  const [searchHistory, setSearchHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSearchHistory();
  }, []);

  const fetchSearchHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Lütfen giriş yapın');
        setLoading(false);
        return;
      }

      const response = await fetch('http://localhost:5050/search-history', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        setSearchHistory(data.search_history);
      } else {
        setError(data.error || 'Geçmiş aramalar yüklenirken hata oluştu');
      }
    } catch (error) {
      setError('Sunucuya bağlanırken hata oluştu');
      console.error('Fetch search history error:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToFavorites = async (searchItem) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5050/favorites', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          search_id: searchItem.id,
          route_name: `${searchItem.origin} - ${searchItem.destination || 'Hedef Belirtilmemiş'}`
        }),
      });

      const data = await response.json();

      if (response.ok) {
        alert('Rota favorilere eklendi! 🌟');
      } else {
        setError(data.error || 'Favorilere eklenirken hata oluştu');
      }
    } catch (error) {
      setError('Sunucuya bağlanırken hata oluştu');
      console.error('Add to favorites error:', error);
    }
  };

  const repeatSearch = async (searchItem) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5050/predict', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          origin: searchItem.origin,
          destination: searchItem.destination,
          datetime: new Date().toISOString()
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Yeni aramayı geçmişe ekle
        await fetch('http://localhost:5050/search-history', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            origin: searchItem.origin,
            destination: searchItem.destination,
            datetime: new Date().toISOString(),
            prediction_result: data
          }),
        });

        alert(`Güncel Trafik Durumu: ${data.traffic_info.description}`);
        
        // Geçmişi yeniden yükle
        fetchSearchHistory();
      } else {
        setError(data.error || 'Trafik tahmini yapılırken hata oluştu');
      }
    } catch (error) {
      setError('Sunucuya bağlanırken hata oluştu');
      console.error('Repeat search error:', error);
    }
  };

  if (loading) {
    return (
      <div style={{
        padding: '2rem',
        textAlign: 'center',
        color: '#6b7280'
      }}>
        Geçmiş aramalar yükleniyor...
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
        📚 Geçmiş Aramalarım
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

      {searchHistory.length === 0 ? (
        <div style={{
          textAlign: 'center',
          color: '#6b7280',
          fontSize: '1.1rem',
          padding: '3rem'
        }}>
          Henüz arama geçmişiniz yok. İlk trafik tahmininizi yapın!
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gap: '1rem'
        }}>
          {searchHistory.map((item) => (
            <div key={item.id} style={{
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
                <div style={{ flex: 1 }}>
                  <h3 style={{
                    fontSize: '1.25rem',
                    fontWeight: '600',
                    color: '#22223b',
                    margin: '0 0 0.5rem 0'
                  }}>
                    {item.origin} {item.destination ? `→ ${item.destination}` : ''}
                  </h3>
                  <p style={{
                    color: '#6b7280',
                    margin: '0 0 0.25rem 0'
                  }}>
                    <strong>Arama Tarihi:</strong> {new Date(item.datetime).toLocaleString('tr-TR')}
                  </p>
                  <p style={{
                    color: '#9ca3af',
                    fontSize: '0.875rem',
                    margin: '0'
                  }}>
                    Kayıt Tarihi: {new Date(item.created_at).toLocaleString('tr-TR')}
                  </p>
                </div>
                <div style={{
                  display: 'flex',
                  gap: '0.5rem',
                  flexDirection: 'column'
                }}>
                  <button
                    onClick={() => repeatSearch(item)}
                    style={{
                      backgroundColor: '#22223b',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      whiteSpace: 'nowrap'
                    }}
                    onMouseOver={(e) => {
                      e.target.style.backgroundColor = '#1a1a2e';
                    }}
                    onMouseOut={(e) => {
                      e.target.style.backgroundColor = '#22223b';
                    }}
                  >
                    🔄 Tekrar Ara
                  </button>
                  <button
                    onClick={() => addToFavorites(item)}
                    style={{
                      backgroundColor: '#f59e0b',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      whiteSpace: 'nowrap'
                    }}
                    onMouseOver={(e) => {
                      e.target.style.backgroundColor = '#d97706';
                    }}
                    onMouseOut={(e) => {
                      e.target.style.backgroundColor = '#f59e0b';
                    }}
                  >
                    ⭐ Favoriye Ekle
                  </button>
                </div>
              </div>

              {item.prediction_result && (
                <div style={{
                  backgroundColor: '#e0f2fe',
                  border: '1px solid #b3e5fc',
                  borderRadius: '6px',
                  padding: '0.75rem',
                  fontSize: '0.875rem'
                }}>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '0.5rem'
                  }}>
                    {(() => {
                      try {
                        const result = typeof item.prediction_result === 'string' 
                          ? JSON.parse(item.prediction_result) 
                          : item.prediction_result;
                        return (
                          <>
                            <div>
                              <strong>Trafik Seviyesi:</strong> {
                                result.traffic_level === 0 ? 'Az' :
                                result.traffic_level === 1 ? 'Orta' : 'Yoğun'
                              }
                            </div>
                            <div>
                              <strong>Açıklama:</strong> {result.traffic_info?.description || 'Bilgi yok'}
                            </div>
                            <div>
                              <strong>Ortalama Hız:</strong> {result.traffic_info?.avg_speed || 'Bilgi yok'} km/h
                            </div>
                            <div>
                              <strong>Araç Sayısı:</strong> {result.traffic_info?.vehicle_count || 'Bilgi yok'}
                            </div>
                          </>
                        );
                      } catch (e) {
                        return <div>Tahmin bilgisi görüntülenemiyor</div>;
                      }
                    })()}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchHistoryPage; 