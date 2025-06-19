// HomePage.js
import React, { useState } from "react";
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

  const navigate = useNavigate();

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

          // Arama geçmişine kaydet
          try {
            const token = localStorage.getItem('token');
            console.log("Token:", token ? "Mevcut" : "Yok");
            
            if (token) {
              const searchData = {
                origin,
                destination,
                datetime: selectedDate.toISOString(),
                prediction_result: response.data
              };
              
              console.log("Gönderilecek veri:", searchData);
              
              const searchResponse = await axios.post("http://localhost:5050/search-history", searchData, {
                headers: {
                  "Content-Type": "application/json",
                  "Authorization": `Bearer ${token}`
                }
              });
              
              console.log("Arama geçmişe kaydedildi:", searchResponse.data);
            } else {
              console.error("Token bulunamadı!");
            }
          } catch (error) {
            console.error("Arama geçmişe kaydedilemedi:", error);
            console.error("Hata detayı:", error.response?.data);
          }
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
        <p style={{ textAlign: "center", color: "#6b7280", marginBottom: 0, fontSize: "1rem" }}>
          Başlangıç ve varış noktası ile gelecek tarih/saat seçin. Trafik parametreleri otomatik hesaplanır.
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
        <LoadScript googleMapsApiKey="google-key">
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
