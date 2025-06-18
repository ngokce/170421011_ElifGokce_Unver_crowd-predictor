# Grafik ve Görselleştirme Kodları - Colab'da sona ekleyin

# Karışıklık matrisi
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Az', 'Orta', 'Yoğun'],
            yticklabels=['Az', 'Orta', 'Yoğun'])
plt.title('Karışıklık Matrisi')
plt.ylabel('Gerçek Değerler')
plt.xlabel('Tahmin Edilen Değerler')
plt.show()

# Özellik önemlilikleri
plt.figure(figsize=(10, 6))
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
})
feature_importance = feature_importance.sort_values('importance', ascending=False)
sns.barplot(x='importance', y='feature', data=feature_importance)
plt.title('Özellik Önemlilikleri')
plt.show()

# Kapsamlı analiz grafikleri
plt.figure(figsize=(20, 15))

# 1. Saatlere göre ortalama hız
plt.subplot(3, 4, 1)
hourly_speed = df.groupby('hour')['AVERAGE_SPEED'].mean()
plt.plot(hourly_speed.index, hourly_speed.values, marker='o', linewidth=2, markersize=6)
plt.title('Saatlere Göre Ortalama Hız')
plt.xlabel('Saat')
plt.ylabel('Ortalama Hız (km/h)')
plt.grid(True, alpha=0.3)
plt.xticks(range(0, 24, 2))

# 2. Günlere göre trafik dağılımı
plt.subplot(3, 4, 2)
day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
daily_traffic = df.groupby(['day_of_week', 'traffic_level']).size().unstack(fill_value=0)
daily_traffic.index = day_names
daily_traffic.plot(kind='bar', stacked=True, color=['green', 'orange', 'red'], ax=plt.gca())
plt.title('Günlere Göre Trafik Dağılımı')
plt.xlabel('Gün')
plt.ylabel('Kayıt Sayısı')
plt.legend(['Az', 'Orta', 'Yoğun'], title='Trafik Seviyesi')
plt.xticks(rotation=45)

# 3. Hız vs Araç sayısı
plt.subplot(3, 4, 3)
sample_df = df.sample(10000)  # Performans için örnekleme
scatter = plt.scatter(sample_df['AVERAGE_SPEED'], sample_df['NUMBER_OF_VEHICLES'], 
                     c=sample_df['traffic_level'], cmap='RdYlGn_r', alpha=0.6)
plt.colorbar(scatter, label='Trafik Seviyesi')
plt.title('Ortalama Hız vs Araç Sayısı')
plt.xlabel('Ortalama Hız (km/h)')
plt.ylabel('Araç Sayısı')

# 4. Aylara göre trafik trendi
plt.subplot(3, 4, 4)
monthly_traffic = df.groupby('month')['traffic_level'].mean()
plt.plot(monthly_traffic.index, monthly_traffic.values, marker='s', linewidth=2, markersize=8)
plt.title('Aylara Göre Trafik Trendi')
plt.xlabel('Ay')
plt.ylabel('Ortalama Trafik Seviyesi')
plt.grid(True, alpha=0.3)
plt.xticks([11, 12, 1], ['Kasım', 'Aralık', 'Ocak'])

# 5. Hafta içi vs Hafta sonu
plt.subplot(3, 4, 5)
weekend_traffic = df.groupby(['is_weekend', 'traffic_level']).size().unstack(fill_value=0)
weekend_traffic.index = ['Hafta içi', 'Hafta sonu']
weekend_traffic.plot(kind='bar', color=['green', 'orange', 'red'], ax=plt.gca())
plt.title('Hafta içi vs Hafta sonu Trafik')
plt.xlabel('Dönem')
plt.ylabel('Kayıt Sayısı')
plt.legend(['Az', 'Orta', 'Yoğun'], title='Trafik Seviyesi')
plt.xticks(rotation=0)

# 6. Trafik seviyesi dağılımı (Pasta)
plt.subplot(3, 4, 6)
traffic_counts = df['traffic_level'].value_counts().sort_index()
colors = ['green', 'orange', 'red']
labels = ['Az Trafik (>50 km/h)', 'Orta Trafik (30-50 km/h)', 'Yoğun Trafik (<30 km/h)']
plt.pie(traffic_counts.values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
plt.title('Trafik Seviyesi Dağılımı')

# 7. Sınıf bazında precision-recall
plt.subplot(3, 4, 7)
from sklearn.metrics import precision_recall_fscore_support
precision, recall, f1, support = precision_recall_fscore_support(y_test, y_pred)

x_pos = np.arange(len(['Az', 'Orta', 'Yoğun']))
width = 0.25

plt.bar(x_pos - width, precision, width, label='Precision', alpha=0.8)
plt.bar(x_pos, recall, width, label='Recall', alpha=0.8)
plt.bar(x_pos + width, f1, width, label='F1-Score', alpha=0.8)

plt.xlabel('Trafik Seviyesi')
plt.ylabel('Skor')
plt.title('Sınıf Bazında Performans')
plt.xticks(x_pos, ['Az', 'Orta', 'Yoğun'])
plt.legend()
plt.ylim(0, 1)

# 8. Tahmin güven dağılımı
plt.subplot(3, 4, 8)
y_pred_proba = model.predict_proba(X_test_scaled)
max_proba = np.max(y_pred_proba, axis=1)
plt.hist(max_proba, bins=20, alpha=0.7, edgecolor='black')
plt.xlabel('Maksimum Tahmin Olasılığı')
plt.ylabel('Frekans')
plt.title('Tahmin Güven Dağılımı')

# 9. Sınıf bazında doğruluk
plt.subplot(3, 4, 9)
class_accuracy = []
for i in range(3):
    mask = y_test == i
    if mask.sum() > 0:
        acc = accuracy_score(y_test[mask], y_pred[mask])
        class_accuracy.append(acc)
    else:
        class_accuracy.append(0)

plt.bar(['Az', 'Orta', 'Yoğun'], class_accuracy, color=['green', 'orange', 'red'], alpha=0.7)
plt.ylabel('Doğruluk')
plt.title('Sınıf Bazında Doğruluk')
plt.ylim(0, 1)

# 10. Hata analizi
plt.subplot(3, 4, 10)
errors = y_test != y_pred
error_by_class = []
for i in range(3):
    mask = y_test == i
    if mask.sum() > 0:
        error_rate = errors[mask].mean()
        error_by_class.append(error_rate)
    else:
        error_by_class.append(0)

plt.bar(['Az', 'Orta', 'Yoğun'], error_by_class, color=['lightcoral', 'lightsalmon', 'lightpink'])
plt.ylabel('Hata Oranı')
plt.title('Sınıf Bazında Hata Oranı')

# 11. Koordinat bazında trafik haritası
plt.subplot(3, 4, 11)
sample_df = df.sample(5000)  # Performans için örnekleme
scatter = plt.scatter(sample_df['LONGITUDE'], sample_df['LATITUDE'], 
                     c=sample_df['traffic_level'], cmap='RdYlGn_r', alpha=0.6, s=1)
plt.colorbar(scatter, label='Trafik Seviyesi')
plt.title('İstanbul Trafik Haritası')
plt.xlabel('Boylam')
plt.ylabel('Enlem')

# 12. Genel performans özeti
plt.subplot(3, 4, 12)
metrics = ['Doğruluk', 'Precision', 'Recall', 'F1-Score']
scores = [accuracy, np.mean(precision), np.mean(recall), np.mean(f1)]

bars = plt.bar(metrics, scores, color=['skyblue', 'lightgreen', 'lightcoral', 'lightyellow'], 
               edgecolor='black', alpha=0.8)
plt.ylabel('Skor')
plt.title('Genel Model Performansı')
plt.ylim(0, 1)

# Bar üzerine değerleri yazdır
for bar, score in zip(bars, scores):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
             f'{score:.3f}', ha='center', va='bottom', fontweight='bold')

plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# Model ve scaler'ı kaydet
print("\n💾 Model ve scaler kaydediliyor...")
joblib.dump(model, "trafik_model.pkl")
joblib.dump(scaler, "scaler.pkl")
print("✅ Model 'trafik_model.pkl' olarak kaydedildi")
print("✅ Scaler 'scaler.pkl' olarak kaydedildi")

# Farklı test senaryoları
print("\n🔮 Farklı senaryolar için tahminler:")

test_scenarios = [
    [8, 1, 0, 11, 15, 45, 500, 41.0082, 28.9784],   # Sabah rush hour
    [17, 1, 0, 11, 10, 30, 800, 41.0082, 28.9784],  # Akşam rush hour
    [14, 6, 1, 11, 40, 80, 200, 41.0082, 28.9784],  # Hafta sonu öğlen
    [2, 2, 0, 11, 60, 100, 50, 41.0082, 28.9784],   # Gece
]

scenario_names = ["Sabah Rush", "Akşam Rush", "Hafta Sonu", "Gece"]

for i, scenario in enumerate(test_scenarios):
    scenario_scaled = scaler.transform([scenario])
    prediction = model.predict(scenario_scaled)[0]
    proba = model.predict_proba(scenario_scaled)[0]
    confidence = max(proba) * 100
    print(f"{scenario_names[i]}: {prediction} ({'Az' if prediction == 0 else 'Orta' if prediction == 1 else 'Yoğun'}) - Güven: {confidence:.1f}%")

# Dosyaları indir
print("\n📥 Model dosyalarını indiriliyor...")
from google.colab import files
files.download("trafik_model.pkl")
files.download("scaler.pkl")

print("\n🎉 Analiz tamamlandı!")
print("📊 Tüm grafikler yukarıda görüntülendi.")
print("💡 Model dosyalarını backend klasörüne koyabilirsiniz.") 