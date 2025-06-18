# CrowdPredictor Database Kurulumu

Bu rehber, CrowdPredictor projesine MySQL database entegrasyonunu tamamlamak için gereken adımları açıklar.

## Kurulum Adımları

### 1. MySQL Bağlantı Bilgilerini Güncelleyin

`backend/app.py` dosyasındaki MySQL bağlantı bilgilerini kendi MySQL sunucunuza göre güncelleyin:

```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # MySQL kullanıcı adınızı girin
    'password': '',  # MySQL şifrenizi girin
    'database': 'traffic_predictor'
}
```

### 2. Database Oluşturun

MySQL komut satırına giriş yapın ve şu komutu çalıştırın:

```bash
mysql -u root -p < backend/setup_database.sql
```

Veya MySQL Workbench gibi GUI araçlarında `backend/setup_database.sql` dosyasını çalıştırın.

### 3. Backend Bağımlılıklarını Yükleyin

```bash
cd backend
pip install -r requirements.txt
```

### 4. Frontend Bağımlılıklarını Yükleyin

```bash
cd traffic-map
npm install
```

### 5. Uygulamayı Başlatın

Backend'i başlatın:
```bash
cd backend
python app.py
```

Frontend'i başlatın (yeni terminal):
```bash
cd traffic-map
npm start
```

## Özellikler

### ✅ Kullanıcı Yönetimi
- Kullanıcı kaydı ve girişi
- JWT token tabanlı authentication
- Güvenli şifre hash'leme

### ✅ Kişiselleştirilmiş Deneyim
- Kişiye özel geçmiş aramalar
- Kişiye özel favoriler
- Her kullanıcı sadece kendi verilerini görebilir

### ✅ Geçmiş Aramalar
- Tüm trafik tahminleri otomatik olarak kaydedilir
- Arama geçmişinden favorilere ekleme
- Geçmiş aramalardan tekrar tahmin yapma

### ✅ Favoriler
- Geçmiş aramalardan favorilere ekleme
- Favori rotaları direkt ekleme
- Favori rotalardan hızlı trafik tahmini

### ✅ Modern UI/UX
- Responsive tasarım
- Kullanıcı dostu interface
- Hata ve başarı mesajları
- Loading durumları

## Database Yapısı

### users
- id (Primary Key)
- name
- email (Unique)
- password_hash
- created_at

### search_history
- id (Primary Key)
- user_id (Foreign Key)
- origin
- destination
- datetime
- prediction_result (JSON)
- created_at

### favorites
- id (Primary Key)
- user_id (Foreign Key)
- origin
- destination
- route_name
- prediction_result (JSON)
- created_at

## API Endpoints

### Authentication
- `POST /register` - Kullanıcı kaydı
- `POST /login` - Kullanıcı girişi

### Trafik Tahmini
- `POST /predict` - Trafik tahmini yap

### Geçmiş Aramalar
- `GET /search-history` - Geçmiş aramaları getir
- `POST /search-history` - Yeni arama ekle

### Favoriler
- `GET /favorites` - Favorileri getir
- `POST /favorites` - Favori ekle
- `DELETE /favorites/{id}` - Favori sil

## Güvenlik Notları

- Şifreler bcrypt ile hash'lenir
- JWT token'lar 24 saat geçerlidir
- Tüm API endpoint'leri token korumalıdır
- Database injection koruması vardır

## Sorun Giderme

1. **Database bağlantı hatası**: MySQL servisinin çalıştığından ve bağlantı bilgilerinin doğru olduğundan emin olun.

2. **Token hatası**: Browser'da localStorage'ı temizleyin veya logout yapıp tekrar login olun.

3. **CORS hatası**: Backend'in localhost:5050'de çalıştığından emin olun.

4. **Frontend yüklenmeme**: Node.js'in güncel sürümünü kullandığınızdan emin olun. 