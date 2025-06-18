# 🚦 CrowdPredictor - İstanbul Trafik Tahmin Sistemi

İstanbul'da trafik yoğunluğunu tahmin eden akıllı web uygulaması. Makine öğrenmesi modeli ile gerçek zamanlı trafik analizi yapabilir, kişisel arama geçmişinizi kaydedebilir ve favori rotalarınızı yönetebilirsiniz.

![Languages](https://img.shields.io/badge/JavaScript-53.1%25-yellow)
![Languages](https://img.shields.io/badge/Python-44.3%25-blue)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange)
![React](https://img.shields.io/badge/Frontend-React-61dafb)
![Flask](https://img.shields.io/badge/Backend-Flask-green)

## ✨ Özellikler

### 🔐 Kullanıcı Sistemi
- Güvenli kayıt ve giriş (JWT Authentication)
- Şifre hash'leme (bcrypt)
- Kişisel veri yönetimi

### 🚗 Trafik Tahmini
- Makine öğrenmesi tabanlı tahmin
- İstanbul'daki popüler lokasyonlar için optimize edilmiş
- Gerçek zamanlı trafik yoğunluğu analizi
- Görsel harita entegrasyonu (Google Maps)

### 📚 Kişisel Veriler
- **Arama Geçmişi:** Tüm trafik tahminlerinizi kaydedin
- **Favoriler:** Sık kullandığınız rotaları hızlı erişim için saklayın
- **Tarih Takibi:** Ne zaman hangi tahmini yaptığınızı görün

### 🎨 Modern UI/UX
- Responsive tasarım
- Kullanıcı dostu arayüz
- Loading states ve error handling
- Mobil uyumlu tasarım

## 🏗️ Teknoloji Stack

### Backend
- **Flask** - Python web framework
- **MySQL** - Veritabanı yönetimi
- **JWT** - Token tabanlı authentication
- **bcrypt** - Şifre güvenliği
- **scikit-learn** - Makine öğrenmesi modeli

### Frontend
- **React** - Kullanıcı arayüzü
- **React Router** - Sayfa yönlendirme
- **Axios** - HTTP client
- **Google Maps API** - Harita entegrasyonu

### Database Schema
```sql
users (id, name, email, password_hash, created_at)
search_history (id, user_id, origin, destination, datetime, prediction_result, created_at)
favorites (id, user_id, origin, destination, route_name, prediction_result, search_datetime, created_at)
```

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- Node.js 14+
- MySQL 8.0+

### Backend Kurulumu
```bash
cd backend
pip install -r requirements.txt
# MySQL veritabanını oluşturun ve app.py'deki MYSQL_CONFIG'i güncelleyin
python app.py
```

### Frontend Kurulumu
```bash
cd traffic-map
npm install
npm start
```

### Database Kurulumu
Detaylı kurulum için: [DATABASE_SETUP.md](DATABASE_SETUP.md)

## 📖 Kullanım

1. **Kayıt Olun** - Yeni hesap oluşturun
2. **Giriş Yapın** - JWT token ile güvenli giriş
3. **Trafik Tahmini** - Başlangıç ve varış noktası seçin
4. **Arama Geçmişi** - Geçmiş tahminlerinizi görüntüleyin
5. **Favoriler** - Sık kullanılan rotaları kaydedin

## 🎯 Proje Hedefleri

- İstanbul trafiğinde daha akıllı seyahat planlaması
- Veri odaklı karar verme desteği
- Kişiselleştirilmiş trafik deneyimi
- Sürdürülebilir ulaşım alışkanlıkları

## 📊 Model Detayları

Trafik tahmin modeli:
- **Random Forest Classifier**
- Saat, gün, mevsim bilgileri
- İstanbul koordinatları
- Rush hour optimizasyonu
- Gerçekçi trafik parametreleri

Detaylı bilgi için: [MODEL_EGITIMI_RAPORU.md](MODEL_EGITIMI_RAPORU.md)

## 🔧 API Endpoints

### Authentication
- `POST /register` - Kullanıcı kaydı
- `POST /login` - Giriş yapma

### Trafik Tahmini
- `POST /predict` - Trafik yoğunluğu tahmini

### Kullanıcı Verileri
- `GET /search-history` - Arama geçmişi
- `POST /search-history` - Yeni arama kaydetme
- `GET /favorites` - Favoriler listesi
- `POST /favorites` - Favori ekleme
- `DELETE /favorites/{id}` - Favori silme

## 📱 Ekran Görüntüleri

### Ana Sayfa - Trafik Tahmini
![Trafik Tahmini](images/ana-sayfa.png)

### Geçmiş Aramalar
![Geçmiş Aramalar](images/gecmis-aramalar.png)

### Favoriler
![Favoriler](images/favoriler.png)

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında dağıtılmaktadır.

## 👨‍💻 Geliştiriciler

[@ngokce](https://github.com/ngokce)
[@namaewasu](https://github.com/namaewasu)
[@mehmetaliyavuzzzz](https://github.com/mehmetaliyavuzzzz)

---