from flask import Flask, request, jsonify
import joblib
import pandas as pd
from datetime import datetime
from flask_cors import CORS
import requests
import geohash  # pip install python-geohash

app = Flask(__name__)
CORS(app)

# Google Geocoding API anahtarınızı buraya ekleyin
GOOGLE_API_KEY = "AIzaSyDOQepkRGNzynm4fxu9u9MN-qfPQcvOVu8"

# Global değişkenler
model = None
scaler = None

# Geçici olarak memory'de tutacağız (sonra database'e geçecek)
user_search_history = {}  # {user_id: [search_records]}
user_favorites = {}       # {user_id: [favorite_records]}


def load_model():
    global model, scaler
    try:
        model = joblib.load("trafik_model.pkl")
        print("✅ Model başarıyla yüklendi")
        
        # Scaler'ı yüklemeyi dene
        try:
            scaler = joblib.load("scaler.pkl")
            print("✅ Scaler başarıyla yüklendi")
        except FileNotFoundError:
            print("⚠️ Scaler dosyası bulunamadı, ölçeklendirme yapılmayacak")
            scaler = None
        
        return True
    except FileNotFoundError:
        print("❌ Model dosyası bulunamadı! Önce modeli eğitin.")
        return False
    except Exception as e:
        print(f"❌ Model yükleme hatası: {str(e)}")
        return False


def get_lat_lng_from_address(address, api_key):
    # İstanbul'daki popüler lokasyonlar için sabit koordinatlar
    location_coords = {
        "maltepe": (40.9333, 29.1333),
        "kadıköy": (40.9917, 29.0270),
        "üsküdar": (41.0214, 29.0161),
        "beşiktaş": (41.0422, 29.0061),
        "şişli": (41.0602, 28.9887),
        "beyoğlu": (41.0370, 28.9857),
        "fatih": (41.0186, 28.9647),
        "bakırköy": (40.9744, 28.8719),
        "zeytinburnu": (41.0058, 28.9019),
        "pendik": (40.8783, 29.2333),
        "kartal": (40.9061, 29.1856),
        "ataşehir": (40.9833, 29.1167),
        "levent": (41.0814, 29.0092),
        "maslak": (41.1086, 29.0219),
        "taksim": (41.0370, 28.9857),
        "sultanahmet": (41.0058, 28.9769),
        "eminönü": (41.0186, 28.9647)
    }
    
    # Adres içinde bilinen lokasyon var mı kontrol et
    address_lower = address.lower()
    for location, coords in location_coords.items():
        if location in address_lower:
            print(f"📍 Bilinen lokasyon kullanıldı: {location}")
            return coords
    
    # Google API'yi dene
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results = response.json().get("results")
            if results:
                location = results[0]["geometry"]["location"]
                print(f"📍 Google API'den koordinat alındı")
                return location["lat"], location["lng"]
    except Exception as e:
        print(f"⚠️ Google API hatası: {str(e)}")
    
    return None, None


def get_traffic_parameters(hour, day_of_week, is_weekend):
    """Saat ve gün bilgisine göre gerçekçi trafik parametreleri üret"""
    
    # Rush hour tanımları
    morning_rush = 7 <= hour <= 9
    evening_rush = 17 <= hour <= 19
    night_time = hour <= 5 or hour >= 23
    
    if is_weekend:
        # Hafta sonu trafiği
        if night_time:
            return {"min_speed": 55, "max_speed": 85, "num_vehicles": 80}
        elif 10 <= hour <= 16:  # Hafta sonu alışveriş saatleri
            return {"min_speed": 35, "max_speed": 65, "num_vehicles": 350}
        else:
            return {"min_speed": 45, "max_speed": 75, "num_vehicles": 200}
    else:
        # Hafta içi trafiği
        if morning_rush or evening_rush:
            # Rush hour - yoğun trafik
            return {"min_speed": 8, "max_speed": 30, "num_vehicles": 750}
        elif night_time:
            # Gece - az trafik
            return {"min_speed": 60, "max_speed": 90, "num_vehicles": 100}
        elif 10 <= hour <= 16:
            # Öğlen saatleri - orta trafik
            return {"min_speed": 25, "max_speed": 55, "num_vehicles": 400}
        else:
            # Diğer saatler - normal trafik
            return {"min_speed": 40, "max_speed": 70, "num_vehicles": 250}

def get_traffic_info_from_prediction(prediction, feature_info):
    """Model çıktısı ve özellik bilgisine göre trafik bilgisini oluştur"""
    
    min_speed = feature_info["min_speed"]
    max_speed = feature_info["max_speed"]
    num_vehicles = feature_info["num_vehicles"]
    hour = feature_info["hour"]
    is_weekend = feature_info["is_weekend"]
    
    # Ortalama hızı hesapla
    avg_speed = (min_speed + max_speed) / 2
    
    if prediction == 0:  # Az trafik
        level = "az"
        color = "green"
        if avg_speed >= 60:
            description = f"Trafik akışı çok iyi - Ortalama hız {avg_speed:.0f} km/h"
        else:
            description = f"Trafik akışı normal - Ortalama hız {avg_speed:.0f} km/h"
            
    elif prediction == 1:  # Orta trafik
        level = "orta"
        color = "yellow"
        if is_weekend:
            description = f"Hafta sonu trafiği - Ortalama hız {avg_speed:.0f} km/h, {num_vehicles} araç"
        elif 7 <= hour <= 9 or 17 <= hour <= 19:
            description = f"Rush hour yaklaşıyor - Ortalama hız {avg_speed:.0f} km/h, {num_vehicles} araç"
        else:
            description = f"Orta yoğunlukta trafik - Ortalama hız {avg_speed:.0f} km/h, {num_vehicles} araç"
            
    else:  # Yoğun trafik (prediction == 2)
        level = "yogun"
        color = "red"
        if 7 <= hour <= 9:
            description = f"Sabah rush hour - Ortalama hız {avg_speed:.0f} km/h, {num_vehicles} araç"
        elif 17 <= hour <= 19:
            description = f"Akşam rush hour - Ortalama hız {avg_speed:.0f} km/h, {num_vehicles} araç"
        else:
            description = f"Yoğun trafik - Ortalama hız {avg_speed:.0f} km/h, {num_vehicles} araç"
    
    return {
        "level": level,
        "color": color,
        "description": description,
        "avg_speed": round(avg_speed, 1),
        "vehicle_count": num_vehicles,
        "speed_range": f"{min_speed}-{max_speed} km/h"
    }

def extract_features_from_request(data):
    dt = pd.to_datetime(data.get("datetime"))
    hour = dt.hour
    day_of_week = dt.dayofweek
    is_weekend = int(day_of_week >= 5)
    month = dt.month

    # Otomatik trafik parametreleri
    traffic_params = get_traffic_parameters(hour, day_of_week, is_weekend)
    min_speed = traffic_params["min_speed"]
    max_speed = traffic_params["max_speed"]
    num_vehicles = traffic_params["num_vehicles"]

    # Adresten koordinat al (Google Geocoding API)
    address = data.get("origin", "Kadıköy, İstanbul")
    lat, lng = get_lat_lng_from_address(address, GOOGLE_API_KEY)
    if lat is None or lng is None:
        # fallback: Kadıköy (sadece API başarısız olursa)
        lat, lng = 40.9917, 29.0270

    features = [
        hour, day_of_week, is_weekend, month,
        min_speed, max_speed, num_vehicles,
        lat, lng
    ]
    
    return features, {
        "hour": hour,
        "day_of_week": day_of_week,
        "is_weekend": bool(is_weekend),
        "month": month,
        "min_speed": min_speed,
        "max_speed": max_speed,
        "num_vehicles": num_vehicles,
        "latitude": lat,
        "longitude": lng,
        "auto_generated": True
    }


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "active",
        "message": "İstanbul Trafik Tahmin API'si",
        "model_loaded": model is not None,
        "endpoints": {
            "/predict": "POST - Trafik tahmini yap",
            "/health": "GET - API sağlık kontrolü",
            "/model-info": "GET - Model bilgileri"
        }
    })


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy" if model is not None else "model_not_loaded",
        "model_available": model is not None,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/model-info", methods=["GET"])
def model_info():
    if model is None:
        return jsonify({"error": "Model yüklenmemiş"}), 400

    return jsonify({
        "model_type": type(model).__name__,
        "feature_count": 10,
        "traffic_levels": {
            0: {"name": "Az", "color": "green", "description": "Trafik akışı normal"},
            1: {"name": "Orta", "color": "yellow", "description": "Trafik yavaşlaması var"},
            2: {"name": "Yoğun", "color": "red", "description": "Trafik çok yoğun"}
        },
        "required_fields": ["origin", "datetime"],
        "note": "Hız aralığı ve araç sayısı otomatik olarak hesaplanır"
    })

@app.route("/test-predict", methods=["POST"])
def test_predict():
    """Test için basit tahmin endpoint'i"""
    if model is None:
        return jsonify({"error": "Model yüklenmemiş"}), 500
    
    try:
        # Sabit test verileri
        test_features = [
            17,  # hour
            1,   # day_of_week (Salı)
            0,   # is_weekend
            1,   # month (Ocak)
            20,  # MINIMUM_SPEED
            60,  # MAXIMUM_SPEED
            300, # NUMBER_OF_VEHICLES
            41.0082, # LATITUDE (İstanbul merkez)
            28.9784  # LONGITUDE
        ]
        
        feature_names = [
            "hour", "day_of_week", "is_weekend", "month",
            "MINIMUM_SPEED", "MAXIMUM_SPEED", "NUMBER_OF_VEHICLES",
            "LATITUDE", "LONGITUDE"
        ]
        
        features_df = pd.DataFrame([test_features], columns=feature_names)
        prediction = model.predict(features_df)[0]
        
        return jsonify({
            "test_features": test_features,
            "prediction": int(prediction),
            "message": "Test tahmini başarılı"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model yüklenmemiş. Lütfen önce modeli eğitin."}), 500

    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"error": "Veri tipi dict değil"}), 400

        required_fields = ["origin", "datetime"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Eksik alan: {field}"}), 400

        features, feature_info = extract_features_from_request(data)

        feature_names = [
            "hour", "day_of_week", "is_weekend", "month",
            "MINIMUM_SPEED", "MAXIMUM_SPEED", "NUMBER_OF_VEHICLES",
            "LATITUDE", "LONGITUDE"
        ]
        features_df = pd.DataFrame([features], columns=feature_names)

        print("🔍 Gelen veri:", data)
        print("🔍 Çıkarılan özellikler:", features)
        print("🔍 Özellik DataFrame:")
        print(features_df)
        
        # Ölçeklendirme varsa uygula
        if scaler is not None:
            features_scaled = scaler.transform(features_df)
            prediction = model.predict(features_scaled)[0]
            print("✅ Özellikler ölçeklendirildi")
        else:
            prediction = model.predict(features_df)[0]
            print("⚠️ Ölçeklendirme yapılmadı")

        # Model çıktısından trafik bilgisini dinamik olarak oluştur
        traffic_info = get_traffic_info_from_prediction(int(prediction), feature_info)

        print("🎯 Tahmin edilen trafik seviyesi:", prediction)
        print("🎯 Trafik info:", traffic_info)

        result = {
            "traffic_level": int(prediction),
            "traffic_info": traffic_info,
            "input_features": feature_info,
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(result)

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Hata detayını terminale yazdırır
        return jsonify({"error": f"Tahmin yapılırken hata oluştu: {str(e)}"}), 500


# Favoriler ve Geçmiş Aramalar için endpoint'ler

@app.route("/search-history/<user_id>", methods=["GET"])
def get_search_history(user_id):
    """Kullanıcının geçmiş aramalarını getir"""
    try:
        history = user_search_history.get(user_id, [])
        return jsonify({
            "user_id": user_id,
            "search_history": history,
            "count": len(history)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search-history", methods=["POST"])
def add_search_history():
    """Yeni arama geçmişine ekle"""
    try:
        data = request.get_json()
        required_fields = ["user_id", "origin", "destination", "datetime"]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Eksik alan: {field}"}), 400
        
        user_id = data["user_id"]
        
        # Arama kaydı oluştur
        search_record = {
            "id": len(user_search_history.get(user_id, [])) + 1,
            "origin": data["origin"],
            "destination": data["destination"],
            "datetime": data["datetime"],
            "search_time": datetime.now().isoformat(),
            "traffic_result": data.get("traffic_result", None)
        }
        
        # Kullanıcının geçmiş aramalarını al veya yeni liste oluştur
        if user_id not in user_search_history:
            user_search_history[user_id] = []
        
        # Yeni aramayı başa ekle (en son arama üstte)
        user_search_history[user_id].insert(0, search_record)
        
        # Maksimum 50 arama tut
        if len(user_search_history[user_id]) > 50:
            user_search_history[user_id] = user_search_history[user_id][:50]
            
        return jsonify({
            "message": "Arama geçmişe eklendi",
            "search_record": search_record
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/favorites/<user_id>", methods=["GET"])
def get_favorites(user_id):
    """Kullanıcının favorilerini getir"""
    try:
        favorites = user_favorites.get(user_id, [])
        return jsonify({
            "user_id": user_id,
            "favorites": favorites,
            "count": len(favorites)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/favorites", methods=["POST"])
def add_favorite():
    """Favori ekle"""
    try:
        data = request.get_json()
        required_fields = ["user_id", "search_id"]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Eksik alan: {field}"}), 400
        
        user_id = data["user_id"]
        search_id = data["search_id"]
        
        # Arama geçmişinden ilgili kaydı bul
        user_history = user_search_history.get(user_id, [])
        search_record = None
        
        for record in user_history:
            if record["id"] == search_id:
                search_record = record
                break
        
        if not search_record:
            return jsonify({"error": "Arama kaydı bulunamadı"}), 404
        
        # Favori kaydı oluştur
        favorite_record = {
            "id": len(user_favorites.get(user_id, [])) + 1,
            "origin": search_record["origin"],
            "destination": search_record["destination"],
            "datetime": search_record["datetime"],
            "search_time": search_record["search_time"],
            "traffic_result": search_record["traffic_result"],
            "favorited_at": datetime.now().isoformat()
        }
        
        # Kullanıcının favorilerini al veya yeni liste oluştur
        if user_id not in user_favorites:
            user_favorites[user_id] = []
        
        # Zaten favorilerde var mı kontrol et
        for fav in user_favorites[user_id]:
            if (fav["origin"] == search_record["origin"] and 
                fav["destination"] == search_record["destination"]):
                return jsonify({"error": "Bu rota zaten favorilerde"}), 400
        
        # Favori ekle
        user_favorites[user_id].append(favorite_record)
        
        return jsonify({
            "message": "Favori eklendi",
            "favorite_record": favorite_record
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/favorites/<user_id>/<int:favorite_id>", methods=["DELETE"])
def remove_favorite(user_id, favorite_id):
    """Favori sil"""
    try:
        if user_id not in user_favorites:
            return jsonify({"error": "Kullanıcının favorisi yok"}), 404
        
        # Favoriyi bul ve sil
        user_favs = user_favorites[user_id]
        for i, fav in enumerate(user_favs):
            if fav["id"] == favorite_id:
                removed_fav = user_favs.pop(i)
                return jsonify({
                    "message": "Favori silindi",
                    "removed_favorite": removed_fav
                })
        
        return jsonify({"error": "Favori bulunamadı"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    if load_model():
        print("🚀 API başlatılıyor...")
        app.run(host="0.0.0.0", port=5050, debug=True)
    else:
        print("❌ Model yüklenemedi. Önce modeli eğitin.")