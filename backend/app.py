from flask import Flask, request, jsonify
import joblib
import pandas as pd
from datetime import datetime, timedelta
from flask_cors import CORS
import requests
import geohash  # pip install python-geohash
import mysql.connector
import json
from mysql.connector import Error
import bcrypt
import jwt
from functools import wraps

app = Flask(__name__)
CORS(app)

# Google Geocoding API anahtarınızı buraya ekleyin
GOOGLE_API_KEY = "google-key"

# JWT secret key (production'da güvenli bir key kullanın)
JWT_SECRET_KEY = "CrowdPredictor_2024_Secret_Key_MySuperSecretKey12345"

# MySQL bağlantı bilgileri
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # MySQL kullanıcı adınızı girin
    'password': '12345',  # MySQL şifrenizi buraya yazın
    'database': 'traffic_predictor'
}

# Global değişkenler
model = None
scaler = None

# Database bağlantısı
def get_db_connection():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    except Error as e:
        print(f"❌ Database bağlantı hatası: {e}")
        return None

# Database tabloları oluştur
def create_tables():
    connection = get_db_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    
    try:
        # Users tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Search history tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            origin VARCHAR(255) NOT NULL,
            destination VARCHAR(255),
            datetime TIMESTAMP NOT NULL,
            prediction_result JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_datetime (user_id, created_at)
        )
        """)
        
        # Favorites tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            origin VARCHAR(255) NOT NULL,
            destination VARCHAR(255),
            route_name VARCHAR(100),
            prediction_result JSON,
            search_datetime DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id)
        )
        """)
        
        # Mevcut tabloya search_datetime sütununu ekle (eğer yoksa)
        try:
            cursor.execute("ALTER TABLE favorites ADD COLUMN search_datetime DATETIME")
            print("✅ Favorites tablosuna search_datetime sütunu eklendi")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("✅ search_datetime sütunu zaten mevcut")
            else:
                print(f"⚠️ ALTER TABLE hatası: {e}")
        
        connection.commit()
        print("✅ Database tabloları başarıyla oluşturuldu")
        return True
        
    except Error as e:
        print(f"❌ Tablo oluşturma hatası: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

# JWT token doğrulama decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token format hatalı'}), 401
        
        if not token:
            return jsonify({'message': 'Token eksik'}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token süresi dolmuş'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Geçersiz token'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated


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


# User Authentication Routes
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([name, email, password]):
            return jsonify({'message': 'Tüm alanlar gereklidir'}), 400
        
        # Şifreyi hash'le
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'message': 'Database bağlantı hatası'}), 500
        
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, password_hash)
            )
            connection.commit()
            
            return jsonify({'message': 'Kullanıcı başarıyla kaydedildi'}), 201
            
        except mysql.connector.IntegrityError:
            return jsonify({'message': 'Bu e-posta adresi zaten kullanılıyor'}), 409
        except Error as e:
            return jsonify({'message': f'Kayıt hatası: {str(e)}'}), 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        return jsonify({'message': f'Sunucu hatası: {str(e)}'}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'message': 'E-posta ve şifre gereklidir'}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'message': 'Database bağlantı hatası'}), 500
        
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                "SELECT id, name, password_hash FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                # JWT token oluştur
                token = jwt.encode({
                    'user_id': user[0],
                    'exp': datetime.utcnow() + timedelta(days=1)
                }, JWT_SECRET_KEY, algorithm='HS256')
                
                return jsonify({
                    'message': 'Giriş başarılı',
                    'token': token,
                    'user': {
                        'id': user[0],
                        'name': user[1],
                        'email': email
                    }
                }), 200
            else:
                return jsonify({'message': 'Geçersiz e-posta veya şifre'}), 401
                
        except Error as e:
            return jsonify({'message': f'Giriş hatası: {str(e)}'}), 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        return jsonify({'message': f'Sunucu hatası: {str(e)}'}), 500

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


# Favoriler ve Geçmiş Aramalar için endpoint'ler (Database entegreli)

@app.route("/search-history", methods=["GET"])
@token_required
def get_search_history(current_user_id):
    """Kullanıcının geçmiş aramalarını getir"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database bağlantı hatası'}), 500
        
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                SELECT id, origin, destination, datetime, prediction_result, created_at
                FROM search_history 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 50
            """, (current_user_id,))
            
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    "id": row[0],
                    "origin": row[1],
                    "destination": row[2],
                    "datetime": row[3].isoformat() if row[3] else None,
                    "prediction_result": row[4],
                    "created_at": row[5].isoformat() if row[5] else None
                })
            
            return jsonify({
                "user_id": current_user_id,
                "search_history": history,
                "count": len(history)
            })
            
        except Error as e:
            return jsonify({'error': f'Geçmiş aramalar getirilemedi: {str(e)}'}), 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search-history", methods=["POST"])
@token_required
def add_search_history(current_user_id):
    """Yeni arama geçmişine ekle"""
    try:
        data = request.get_json()
        required_fields = ["origin", "datetime"]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Eksik alan: {field}"}), 400
        
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database bağlantı hatası'}), 500
        
        cursor = connection.cursor()
        
        try:
            # Datetime'ı MySQL formatına çevir
            from datetime import datetime
            iso_datetime = data["datetime"]
            # UTC'yi yerel saat olarak işle (kullanıcının seçtiği tarih/saat)
            if iso_datetime.endswith('Z'):
                iso_datetime = iso_datetime[:-1]  # Z'yi kaldır
            mysql_datetime = datetime.fromisoformat(iso_datetime).strftime('%Y-%m-%d %H:%M:%S')
            
            # Arama kaydını database'e ekle
            cursor.execute("""
                INSERT INTO search_history (user_id, origin, destination, datetime, prediction_result)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                current_user_id,
                data["origin"],
                data.get("destination", ""),
                mysql_datetime,
                json.dumps(data.get("prediction_result", None))
            ))
            
            connection.commit()
            search_id = cursor.lastrowid
            
            return jsonify({
                "message": "Arama geçmişe eklendi",
                "search_id": search_id
            })
            
        except Error as e:
            return jsonify({'error': f'Arama geçmişe eklenemedi: {str(e)}'}), 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/favorites", methods=["GET"])
@token_required
def get_favorites(current_user_id):
    """Kullanıcının favorilerini getir"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database bağlantı hatası'}), 500
        
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                SELECT id, origin, destination, route_name, prediction_result, search_datetime, created_at
                FROM favorites 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """, (current_user_id,))
            
            rows = cursor.fetchall()
            
            favorites = []
            for row in rows:
                favorites.append({
                    "id": row[0],
                    "origin": row[1],
                    "destination": row[2],
                    "route_name": row[3],
                    "prediction_result": row[4],
                    "search_datetime": row[5].isoformat() if row[5] else None,
                    "created_at": row[6].isoformat() if row[6] else None
                })
            
            return jsonify({
                "user_id": current_user_id,
                "favorites": favorites,
                "count": len(favorites)
            })
            
        except Error as e:
            return jsonify({'error': f'Favoriler getirilemedi: {str(e)}'}), 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/favorites", methods=["POST"])
@token_required
def add_favorite(current_user_id):
    """Favori ekle (geçmiş aramalardan veya direkt)"""
    try:
        data = request.get_json()
        
        # Geçmiş aramalardan ekleme
        if "search_id" in data:
            search_id = data["search_id"]
            
            connection = get_db_connection()
            if connection is None:
                return jsonify({'error': 'Database bağlantı hatası'}), 500
            
            cursor = connection.cursor()
            
            try:
                # Arama geçmişinden kaydı al
                cursor.execute("""
                    SELECT origin, destination, datetime, prediction_result
                    FROM search_history 
                    WHERE id = %s AND user_id = %s
                """, (search_id, current_user_id))
                
                search_record = cursor.fetchone()
                
                if not search_record:
                    return jsonify({"error": "Arama kaydı bulunamadı"}), 404
                
                # Zaten favorilerde var mı kontrol et
                cursor.execute("""
                    SELECT id FROM favorites 
                    WHERE user_id = %s AND origin = %s AND destination = %s
                """, (current_user_id, search_record[0], search_record[1]))
                
                if cursor.fetchone():
                    return jsonify({"error": "Bu rota zaten favorilerde"}), 400
                
                # Favori ekle
                route_name = data.get("route_name", f"{search_record[0]} - {search_record[1]}")
                cursor.execute("""
                    INSERT INTO favorites (user_id, origin, destination, route_name, prediction_result, search_datetime)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    current_user_id,
                    search_record[0],
                    search_record[1],
                    route_name,
                    json.dumps(search_record[3]),
                    search_record[2]  # datetime from search_history
                ))
                
                connection.commit()
                favorite_id = cursor.lastrowid
                
                return jsonify({
                    "message": "Favori eklendi",
                    "favorite_id": favorite_id
                })
                
            except Error as e:
                return jsonify({'error': f'Favori eklenemedi: {str(e)}'}), 500
            finally:
                cursor.close()
                connection.close()
        
        # Direkt favori ekleme
        else:
            required_fields = ["origin", "destination"]
            
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Eksik alan: {field}"}), 400
            
            connection = get_db_connection()
            if connection is None:
                return jsonify({'error': 'Database bağlantı hatası'}), 500
            
            cursor = connection.cursor()
            
            try:
                # Zaten favorilerde var mı kontrol et
                cursor.execute("""
                    SELECT id FROM favorites 
                    WHERE user_id = %s AND origin = %s AND destination = %s
                """, (current_user_id, data["origin"], data["destination"]))
                
                if cursor.fetchone():
                    return jsonify({"error": "Bu rota zaten favorilerde"}), 400
                
                # Favori ekle
                route_name = data.get("route_name", f"{data['origin']} - {data['destination']}")
                cursor.execute("""
                    INSERT INTO favorites (user_id, origin, destination, route_name, prediction_result, search_datetime)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    current_user_id,
                    data["origin"],
                    data["destination"],
                    route_name,
                    json.dumps(data.get("prediction_result", None)),
                    None  # No search datetime for direct add
                ))
                
                connection.commit()
                favorite_id = cursor.lastrowid
                
                return jsonify({
                    "message": "Favori eklendi",
                    "favorite_id": favorite_id
                })
                
            except Error as e:
                return jsonify({'error': f'Favori eklenemedi: {str(e)}'}), 500
            finally:
                cursor.close()
                connection.close()
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/favorites/<int:favorite_id>", methods=["DELETE"])
@token_required
def remove_favorite(current_user_id, favorite_id):
    """Favori sil"""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database bağlantı hatası'}), 500
        
        cursor = connection.cursor()
        
        try:
            # Favori var mı kontrol et ve sil
            cursor.execute("""
                DELETE FROM favorites 
                WHERE id = %s AND user_id = %s
            """, (favorite_id, current_user_id))
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Favori bulunamadı"}), 404
            
            connection.commit()
            
            return jsonify({
                "message": "Favori silindi",
                "favorite_id": favorite_id
            })
            
        except Error as e:
            return jsonify({'error': f'Favori silinemedi: {str(e)}'}), 500
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Database tablolarını oluştur
    if create_tables():
        print("✅ Database tabloları hazır")
    else:
        print("⚠️ Database tabloları oluşturulamadı, devam ediliyor...")
    
    if load_model():
        print("🚀 API başlatılıyor...")
        app.run(host="0.0.0.0", port=5050, debug=True)
    else:
        print("❌ Model yüklenemedi. Önce modeli eğitin.")
