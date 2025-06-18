// HomePage.js
import React, { useState, useEffect } from "react";
import { GoogleMap, LoadScript, DirectionsRenderer } from "@react-google-maps/api";
import axios from "axios";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { useNavigate } from "react-router-dom";

const center = { lat: 41.0082, lng: 28.9784 };

const HomePage = () => {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [directions, setDirections] = useState(null);
  const [routeColor, setRouteColor] = useState("gray");
  const [searchHistory, setSearchHistory] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [activeTab, setActiveTab] = useState("search"); // search, history, favorites
  const [userId] = useState(() => {
    // Geçici kullanıcı ID'si - daha sonra login sistemiyle entegre edilecek
    let id = localStorage.getItem("userId");
    if (!id) {
      id = "user_" + Math.random().toString(36).substr(2, 9);
      localStorage.setItem("userId", id);
    }
    return id;
  });

  const navigate = useNavigate();

  // Sayfa yüklendiğinde geçmiş aramalar ve favorileri getir
  useEffect(() => {
    fetchSearchHistory();
    fetchFavorites();
  }, []);

  const fetchSearchHistory = async () => {
    try {
      const response = await axios.get(`http://localhost:5050/search-history/${userId}`);
      setSearchHistory(response.data.search_history);
    } catch (error) {
      console.error("Geçmiş aramalar getirilemedi:", error);
    }
  };

  const fetchFavorites = async () => {
    try {
      const response = await axios.get(`http://localhost:5050/favorites/${userId}`);
      setFavorites(response.data.favorites);
    } catch (error) {
      console.error("Favoriler getirilemedi:", error);
    }
  };

  const addToSearchHistory = async (searchData) => {
    try {
      await axios.post("http://localhost:5050/search-history", {
        user_id: userId,
        origin: searchData.origin,
        destination: searchData.destination,
        datetime: searchData.datetime,
        traffic_result: searchData.traffic_result
      });
      fetchSearchHistory(); // Listeyi güncelle
    } catch (error) {
      console.error("Arama geçmişe eklenemedi:", error);
    }
  };

  const addToFavorites = async (searchId) => {
    try {
      await axios.post("http://localhost:5050/favorites", {
        user_id: userId,
        search_id: searchId
      });
      fetchFavorites(); // Favoriler listesini güncelle
      alert("Favori eklendi!");
    } catch (error) {
      console.error("Favori eklenemedi:", error);
      alert("Favori eklenirken hata oluştu: " + (error.response?.data?.error || "Bilinmeyen hata"));
    }
  };

  const removeFromFavorites = async (favoriteId) => {
    try {
      await axios.delete(`http://localhost:5050/favorites/${userId}/${favoriteId}`);
      fetchFavorites(); // Favoriler listesini güncelle
      alert("Favori silindi!");
    } catch (error) {
      console.error("Favori silinemedi:", error);
      alert("Favori silinirken hata oluştu");
    }
  };

  const useSearchFromHistory = (searchRecord) => {
    setOrigin(searchRecord.origin);
    setDestination(searchRecord.destination);
    setSelectedDate(new Date(searchRecord.datetime));
    setActiveTab("search");
  };

  const handleSubmit = async () => {
    if (!origin || !destination) return alert("Başlangıç ve varış noktası girin!");

    console.log("Origin:", origin, "Destination:", destination);

    const directionsService = new window.google.maps.DirectionsService();

    directionsService.route(
      {
        origin,
        destination,
        travelMode: window.google.maps.TravelMode.DRIVING,
      },
      async (result, status) => {
        if (status === "OK") {
          setDirections(result);

          const response = await axios.post("http://localhost:5050/predict", {
            origin,
            destination,
            datetime: selectedDate.toISOString()
          }, {
            headers: {
              "Content-Type": "application/json"
            }
          });

          const colorMap = {
            0: "green",
            1: "yellow",
            2: "red"
          };
          const trafficLevel = response.data.traffic_level;
          const color = colorMap[trafficLevel] || "gray";
          setRouteColor(color);

          // Arama geçmişine ekle
          const searchData = {
            origin,
            destination,
            datetime: selectedDate.toISOString(),
            traffic_result: response.data
          };
          addToSearchHistory(searchData);
        } else {
          alert("Rota bulunamadı.");
        }
      }
    );
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #232526 0%, #414345 100%)",
        display: "flex",
        padding: "2rem",
        gap: "2rem"
      }}
    >
      <div
        style={{
          background: "rgba(255,255,255,0.97)",
          borderRadius: 18,
          boxShadow: "0 8px 32px rgba(0,0,0,0.18)",
          padding: "2rem",
          width: "450px",
          height: "fit-content",
          display: "flex",
          flexDirection: "column",
          gap: "1.2rem"
        }}
      >
        <h2 style={{ textAlign: "center", color: "#22223b", fontWeight: 700, fontSize: "1.8rem", letterSpacing: 1 }}>
          🚦 Trafik Yoğunluğu Tahmini
        </h2>

        {/* Tab Navigation */}
        <div style={{ display: "flex", borderBottom: "1px solid #e5e7eb", marginBottom: "1rem" }}>
          <button 
            onClick={() => setActiveTab("search")}
            style={{
              flex: 1,
              padding: "0.8rem",
              border: "none",
              background: activeTab === "search" ? "#8A2BE2" : "transparent",
              color: activeTab === "search" ? "white" : "#6b7280",
              borderRadius: "8px 8px 0 0",
              cursor: "pointer",
              fontSize: "0.9rem",
              fontWeight: 600
            }}
          >
            🔍 Arama
          </button>
          <button 
            onClick={() => setActiveTab("history")}
            style={{
              flex: 1,
              padding: "0.8rem",
              border: "none",
              background: activeTab === "history" ? "#8A2BE2" : "transparent",
              color: activeTab === "history" ? "white" : "#6b7280",
              cursor: "pointer",
              fontSize: "0.9rem",
              fontWeight: 600
            }}
          >
            📝 Geçmiş ({searchHistory.length})
          </button>
          <button 
            onClick={() => setActiveTab("favorites")}
            style={{
              flex: 1,
              padding: "0.8rem",
              border: "none",
              background: activeTab === "favorites" ? "#8A2BE2" : "transparent",
              color: activeTab === "favorites" ? "white" : "#6b7280",
              borderRadius: "0 0 8px 8px",
              cursor: "pointer",
              fontSize: "0.9rem",
              fontWeight: 600
            }}
          >
            ⭐ Favoriler ({favorites.length})
          </button>
        </div>

        {/* Search Tab Content */}
        {activeTab === "search" && (
          <>
            <p style={{ textAlign: "center", color: "#6b7280", marginBottom: 0, fontSize: "0.9rem" }}>
              Başlangıç ve varış noktası ile gelecek tarih/saat seçin.
            </p>
            
            <div style={{ position: "relative" }}>
              <input
                style={{
                  width: "90%",
                  padding: "0.8rem 1rem",
                  borderRadius: 8,
                  border: "1px solid #e5e7eb",
                  fontSize: "1rem",
                  background: "#f9fafb",
                  color: "#22223b",
                  outline: "none"
                }}
                placeholder="Başlangıç noktası"
                value={origin}
                onChange={e => setOrigin(e.target.value)}
              />
            </div>

            <div style={{ position: "relative" }}>
              <input
                style={{
                  width: "90%",
                  padding: "0.8rem 1rem",
                  borderRadius: 8,
                  border: "1px solid #e5e7eb",
                  fontSize: "1rem",
                  background: "#f9fafb",
                  color: "#22223b",
                  outline: "none"
                }}
                placeholder="Varış noktası"
                value={destination}
                onChange={e => setDestination(e.target.value)}
              />
            </div>

            <div style={{ position: "relative" }}>
              <DatePicker
                selected={selectedDate}
                onChange={date => setSelectedDate(date)}
                showTimeSelect
                dateFormat="Pp"
                customInput={
                  <input
                    style={{
                      width: "100%",
                      padding: "0.8rem 1rem",
                      borderRadius: 8,
                      border: "1px solid #e5e7eb",
                      fontSize: "1rem",
                      background: "#f9fafb",
                      color: "#22223b",
                      outline: "none"
                    }}
                    placeholder="Tarih ve saat seç"
                    readOnly
                  />
                }
              />
            </div>

            <button
              onClick={handleSubmit}
              style={{
                background: "linear-gradient(90deg, #8A2BE2 0%, #4B0082 100%)",
                color: "#fff",
                padding: "0.9rem 1.5rem",
                borderRadius: 8,
                border: "none",
                fontSize: "1.1rem",
                fontWeight: 600,
                cursor: "pointer",
                boxShadow: "0 2px 8px rgba(138,43,226,0.08)",
                transition: "all 0.2s"
              }}
            >
              Haritada Göster
            </button>
          </>
        )}

        {/* Search History Tab Content */}
        {activeTab === "history" && (
          <div style={{ maxHeight: "400px", overflowY: "auto" }}>
            <p style={{ textAlign: "center", color: "#6b7280", marginBottom: "1rem", fontSize: "0.9rem" }}>
              Geçmiş aramalarınız ({searchHistory.length})
            </p>
            
            {searchHistory.length === 0 ? (
              <div style={{ textAlign: "center", color: "#9ca3af", padding: "2rem" }}>
                <p>📝 Henüz arama yapmadınız</p>
                <p style={{ fontSize: "0.8rem" }}>İlk aramanızı yapmak için 'Arama' sekmesine geçin</p>
              </div>
            ) : (
              searchHistory.map((search, index) => (
                <div key={search.id} style={{
                  border: "1px solid #e5e7eb",
                  borderRadius: 8,
                  padding: "1rem",
                  marginBottom: "0.5rem",
                  background: "#f9fafb"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: "600", color: "#22223b", fontSize: "0.9rem" }}>
                        📍 {search.origin} → {search.destination}
                      </div>
                      <div style={{ color: "#6b7280", fontSize: "0.8rem", marginTop: "0.3rem" }}>
                        🕒 {new Date(search.datetime).toLocaleString('tr-TR')}
                      </div>
                      {search.traffic_result && (
                        <div style={{ marginTop: "0.3rem" }}>
                          <span style={{
                            display: "inline-block",
                            width: "12px",
                            height: "12px",
                            borderRadius: "50%",
                            background: search.traffic_result.traffic_info?.color || "gray",
                            marginRight: "0.5rem"
                          }}></span>
                          <span style={{ fontSize: "0.8rem", color: "#6b7280" }}>
                            {search.traffic_result.traffic_info?.level || "Bilinmeyen"}
                          </span>
                        </div>
                      )}
                    </div>
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <button
                        onClick={() => useSearchFromHistory(search)}
                        style={{
                          background: "#e5e7eb",
                          border: "none",
                          borderRadius: 4,
                          padding: "0.3rem 0.6rem",
                          cursor: "pointer",
                          fontSize: "0.8rem"
                        }}
                      >
                        🔄 Kullan
                      </button>
                      <button
                        onClick={() => addToFavorites(search.id)}
                        style={{
                          background: "#fbbf24",
                          border: "none",
                          borderRadius: 4,
                          padding: "0.3rem 0.6rem",
                          cursor: "pointer",
                          fontSize: "0.8rem",
                          color: "white"
                        }}
                      >
                        ⭐ Favori
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Favorites Tab Content */}
        {activeTab === "favorites" && (
          <div style={{ maxHeight: "400px", overflowY: "auto" }}>
            <p style={{ textAlign: "center", color: "#6b7280", marginBottom: "1rem", fontSize: "0.9rem" }}>
              Favori rotalarınız ({favorites.length})
            </p>
            
            {favorites.length === 0 ? (
              <div style={{ textAlign: "center", color: "#9ca3af", padding: "2rem" }}>
                <p>⭐ Henüz favori rotanız yok</p>
                <p style={{ fontSize: "0.8rem" }}>Geçmiş aramalar sekmesinden rotaları favorilere ekleyebilirsiniz</p>
              </div>
            ) : (
              favorites.map((favorite, index) => (
                <div key={favorite.id} style={{
                  border: "1px solid #fbbf24",
                  borderRadius: 8,
                  padding: "1rem",
                  marginBottom: "0.5rem",
                  background: "#fffbeb"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: "600", color: "#22223b", fontSize: "0.9rem" }}>
                        ⭐ {favorite.origin} → {favorite.destination}
                      </div>
                      <div style={{ color: "#6b7280", fontSize: "0.8rem", marginTop: "0.3rem" }}>
                        🕒 {new Date(favorite.datetime).toLocaleString('tr-TR')}
                      </div>
                      <div style={{ color: "#6b7280", fontSize: "0.8rem" }}>
                        💫 Favoriye eklendi: {new Date(favorite.favorited_at).toLocaleString('tr-TR')}
                      </div>
                      {favorite.traffic_result && (
                        <div style={{ marginTop: "0.3rem" }}>
                          <span style={{
                            display: "inline-block",
                            width: "12px",
                            height: "12px",
                            borderRadius: "50%",
                            background: favorite.traffic_result.traffic_info?.color || "gray",
                            marginRight: "0.5rem"
                          }}></span>
                          <span style={{ fontSize: "0.8rem", color: "#6b7280" }}>
                            {favorite.traffic_result.traffic_info?.level || "Bilinmeyen"}
                          </span>
                        </div>
                      )}
                    </div>
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <button
                        onClick={() => useSearchFromHistory(favorite)}
                        style={{
                          background: "#e5e7eb",
                          border: "none",
                          borderRadius: 4,
                          padding: "0.3rem 0.6rem",
                          cursor: "pointer",
                          fontSize: "0.8rem"
                        }}
                      >
                        🔄 Kullan
                      </button>
                      <button
                        onClick={() => removeFromFavorites(favorite.id)}
                        style={{
                          background: "#ef4444",
                          border: "none",
                          borderRadius: 4,
                          padding: "0.3rem 0.6rem",
                          cursor: "pointer",
                          fontSize: "0.8rem",
                          color: "white"
                        }}
                      >
                        🗑️ Sil
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Trafik Renk Göstergesi - Sadece Arama Sekmesinde */}
        {activeTab === "search" && (
          <div style={{ display: "flex", justifyContent: "center", gap: 16, marginTop: 8 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ width: 14, height: 14, borderRadius: 7, background: "green", display: "inline-block" }}></span>
              <span style={{ color: "#22223b", fontSize: "0.9rem" }}>Az</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ width: 14, height: 14, borderRadius: 7, background: "yellow", display: "inline-block", border: "1px solid #ccc" }}></span>
              <span style={{ color: "#22223b", fontSize: "0.9rem" }}>Orta</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ width: 14, height: 14, borderRadius: 7, background: "red", display: "inline-block" }}></span>
              <span style={{ color: "#22223b", fontSize: "0.9rem" }}>Yoğun</span>
            </div>
          </div>
        )}
      </div>

      <div
        style={{
          flex: 1,
          height: "calc(100vh - 4rem)",
          borderRadius: 18,
          overflow: "hidden",
          boxShadow: "0 8px 32px rgba(0,0,0,0.18)",
          background: "#fff"
        }}
      >
        <LoadScript googleMapsApiKey="AIzaSyDOQepkRGNzynm4fxu9u9MN-qfPQcvOVu8">
          <GoogleMap mapContainerStyle={{ height: "100%", width: "100%" }} center={center} zoom={12}>
            {directions && (
              <DirectionsRenderer
                key={routeColor}
                directions={directions}
                options={{
                  polylineOptions: {
                    strokeColor: routeColor,
                    strokeWeight: 6
                  }
                }}
              />
            )}
          </GoogleMap>
        </LoadScript>
      </div>
    </div>
  );
};

export default HomePage;