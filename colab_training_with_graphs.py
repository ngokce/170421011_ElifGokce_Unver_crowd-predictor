# Google Colab'da Trafik Tahmin Modeli Eğitimi ve Görselleştirme
# Bu kodu Google Colab'da çalıştırın

# Gerekli kütüphaneleri içe aktar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import precision_recall_curve, roc_curve, auc
import joblib
import warnings
warnings.filterwarnings('ignore')

# Grafik ayarları
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

print("🚀 Trafik Tahmin Modeli Eğitimi ve Analizi Başlıyor...")
print("=" * 60)

# Veri dosyalarını yükle
dosyalar = [
    "ibb_traffic_2024_11.csv",
    "ibb_traffic_2024_12.csv",
    "ibb_traffic_2025_01.csv"
]

print(f"📋 Yüklenecek dosyalar: {dosyalar}")
print("-" * 40)

# Verileri birleştir
df_list = []
for dosya in dosyalar:
    try:
        df = pd.read_csv(dosya)
        df_list.append(df)
        print(f"✅ {dosya} başarıyla yüklendi - {df.shape[0]} satır, {df.shape[1]} sütun")
    except Exception as e:
        print(f"❌ {dosya} yüklenirken hata: {str(e)}")

if df_list:
    df = pd.concat(df_list, ignore_index=True)
    print(f"\n📊 Birleştirilmiş veri seti boyutu: {df.shape[0]} satır, {df.shape[1]} sütun")
else:
    print("❌ Hiç dosya yüklenemedi!")
    exit()

# Veri sözlüğüne göre sütun kontrolü
expected_columns = ['DATE_TIME', 'LATITUDE', 'LONGITUDE', 'GEOHASH', 
                   'MINIMUM_SPEED', 'MAXIMUM_SPEED', 'AVERAGE_SPEED', 'NUMBER_OF_VEHICLES']

print("\n🔍 Sütun kontrolü:")
missing_columns = [col for col in expected_columns if col not in df.columns]
if missing_columns:
    print(f"❌ Eksik sütunlar: {missing_columns}")
    print(f"📋 Mevcut sütunlar: {list(df.columns)}")
else:
    print("✅ Tüm gerekli sütunlar mevcut")

# Veri tiplerini kontrol et ve düzenle
print("\n🔧 Veri tipleri düzenleniyor...")
df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')
df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
df['MINIMUM_SPEED'] = pd.to_numeric(df['MINIMUM_SPEED'], errors='coerce')
df['MAXIMUM_SPEED'] = pd.to_numeric(df['MAXIMUM_SPEED'], errors='coerce')
df['AVERAGE_SPEED'] = pd.to_numeric(df['AVERAGE_SPEED'], errors='coerce')
df['NUMBER_OF_VEHICLES'] = pd.to_numeric(df['NUMBER_OF_VEHICLES'], errors='coerce')

# Eksik değerleri temizle
df = df.dropna()
print(f"✅ Temizlenen veri: {df.shape[0]} satır")

# Veri özeti
print("\n📈 VERİ ÖZETİ:")
print("-" * 30)
print(f"📅 Tarih aralığı: {df['DATE_TIME'].min()} - {df['DATE_TIME'].max()}")
print(f"🗺️  Koordinat aralığı: Lat({df['LATITUDE'].min():.4f} - {df['LATITUDE'].max():.4f})")
print(f"    Lon({df['LONGITUDE'].min():.4f} - {df['LONGITUDE'].max():.4f})")
print(f"🚗 Hız aralığı: {df['AVERAGE_SPEED'].min():.1f} - {df['AVERAGE_SPEED'].max():.1f} km/h")
print(f"🚙 Araç sayısı: {df['NUMBER_OF_VEHICLES'].min()} - {df['NUMBER_OF_VEHICLES'].max()}")
print(f"📍 Benzersiz GEOHASH: {df['GEOHASH'].nunique()}")

# Veri ön işleme
print("\n🔍 Veri ön işleme başlıyor...")

# Zaman özelliklerini oluştur
df["timestamp"] = pd.to_datetime(df["DATE_TIME"])
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek
df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
df["month"] = df["timestamp"].dt.month

# Trafik seviyesi sınıflandırması - Daha dengeli eşikler
def classify_traffic(avg_speed):
    if avg_speed <= 30:      # Daha yüksek eşik
        return 2  # Yoğun
    elif avg_speed <= 50:    # Daha yüksek eşik
        return 1  # Orta
    else:
        return 0  # Az

df["traffic_level"] = df["AVERAGE_SPEED"].apply(classify_traffic)

# Sınıf dağılımını kontrol et
print("\n📊 Sınıf dağılımı:")
traffic_counts = df["traffic_level"].value_counts().sort_index()
for level, count in traffic_counts.items():
    level_name = ['Az', 'Orta', 'Yoğun'][level]
    print(f"  {level} ({level_name}): {count:,} ({count/len(df)*100:.1f}%)")

# Veri dengesizliğini düzelt
print("\n⚖️ Veri dengesizliği düzeltiliyor...")
df_0 = df[df["traffic_level"] == 0]
df_1 = df[df["traffic_level"] == 1]
df_2 = df[df["traffic_level"] == 2]

n = min(len(df_0), len(df_1), len(df_2))
print(f"Her sınıf için {n:,} örnek kullanılacak")

df_balanced = pd.concat([
    df_0.sample(n=n, random_state=42),
    df_1.sample(n=n, random_state=42),
    df_2.sample(n=n, random_state=42)
]).sample(frac=1, random_state=42)

print(f"✅ Dengeli veri seti: {df_balanced.shape[0]:,} satır")

# Özellik seçimi
features = [
    "hour", "day_of_week", "is_weekend", "month",
    "MINIMUM_SPEED", "MAXIMUM_SPEED", "NUMBER_OF_VEHICLES",
    "LATITUDE", "LONGITUDE"
]

X = df_balanced[features]
y = df_balanced["traffic_level"]

# Veriyi böl
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\n📊 Eğitim seti: {X_train.shape[0]:,} örnek")
print(f"📊 Test seti: {X_test.shape[0]:,} örnek")

# Özellik ölçeklendirme
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model eğitimi - Daha iyi parametreler
print("\n🤖 Model eğitimi başlıyor...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1  # Paralel işlem
)
model.fit(X_train_scaled, y_train)
print("✅ Model eğitimi tamamlandı!")

# Model değerlendirmesi
print("\n📊 Model performansı:")
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"🎯 Doğruluk: {accuracy:.3f} ({accuracy*100:.1f}%)")
print("\n📋 Detaylı Rapor:")
print(classification_report(y_test, y_pred, target_names=['Az', 'Orta', 'Yoğun'])) 