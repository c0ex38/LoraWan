# LoRaWAN Simülasyon Konfigürasyon Modülü

# -- Fiziksel Katman (PHY) Parametreleri --
DEFAULT_BW = 125  # Bant Genişliği (kHz) - Standart LoRaWAN kanalı
DEFAULT_CR = 1    # Kodlama Oranı (4/5) - Hata düzeltme kapasitesi
PREAMBLE_LEN = 8  # Giriş sembol sayısı

# -- Enerji Tüketim Parametreleri --
TX_CURRENT_MA = 120.0     # İletim anındaki akım (mA)
SLEEP_CURRENT_UA = 2.0    # Uyku modundaki akım (uA)
OPERATING_VOLTAGE = 3.3   # Çalışma gerilimi (Volt)
BATTERY_CAPACITY_MAH = 2500 # Pil kapasitesi (mAh)

# -- Sinyal ve Hassasiyet Eşikleri (SX1276 Sensör Verileri) --
# Her Spreading Factor (SF) için alıcının duyabileceği minimum sinyal seviyesi (dBm)
SF_SENSITIVITY = {
    7: -123,
    8: -126,
    9: -129,
    10: -132,
    11: -134.5,
    12: -137
}

# Başarılı iletişim için gereken minimum Sinyal-Gürültü Oranı (SNR)
REQUIRED_SNR = {
    7: -7.5,
    8: -10,
    9: -12.5,
    10: -15,
    11: -17.5,
    12: -20
}

# -- Protokol Kısıtları (EU868 Avrupa Standartları) --
DUTY_CYCLE_LIMIT = 0.01  # %1 Görev Döngüsü - Yasal iletim sınırı
MTU_LIMITS = {
    7: 222,
    8: 222,
    9: 115,
    10: 51,
    11: 51,
    12: 51
}

# -- SIR / Rejection Matrix (SF'ler Arası Girişim Analizi) --
# p1 paketinin, p2 girişimine rağmen duyulabilmesi için gereken SIR eşik değerleri
REJECTION_MATRIX = {
    7:  {8: -16, 9: -18, 10: -20, 11: -22, 12: -25},
    8:  {7: -16, 9: -16, 10: -18, 11: -20, 12: -22},
    9:  {7: -18, 8: -16, 10: -16, 11: -18, 12: -20},
    10: {7: -20, 8: -18, 9: -16, 11: -16, 12: -18},
    11: {7: -22, 8: -20, 9: -18, 10: -16, 12: -16},
    12: {7: -25, 8: -22, 9: -20, 10: -18, 11: -16}
}

# -- Çakışma ve Yakalama Etkisi (Capture Effect) --
# Aynı kanalda gelen iki paketten biri diğerinden 6dB güçlüyse, güçlü olan 'yakalanabilir'.
CAPTURE_EFFECT_THRESHOLD = 6.0  

# -- Ağ ve Şehir Ayarları --
NUM_CHANNELS = 8           # Toplam frekans kanalı sayısı
MAX_GATEWAYS = 20          # Simülasyonun desteklediği maksimum Gateway kapasitesi
MIN_RSSI_THRESHOLD = -130  # Bir paketin gateway tarafından algılanabilmesi için min. RSSI

# -- Senaryo ve Kaos Parametreleri --
PATH_LOSS_EXPONENT = 3.0    # Yol kaybı üssü (Şehir içi ortam için 3.0-4.0)
SHADOWING_STD_NORMAL = 6.0  # Normal havada standart sapma (dB)
SHADOWING_STD_STORM = 12.0  # Fırtınalı havada standart sapma (dB)
JAMMER_RADIUS = 500         # Sinyal karıştırıcının etki yarıçapı (metre)
JAMMER_POWER_DB = 30        # Karıştırıcının sinyal bastırma gücü (dB)
CHAOS_FAILURE_CHANCE = 0.05 # Kaos modunda cihazın rastgele bozulma ihtimali (%5)
ACK_PAYLOAD_BYTES = 10      # Gateway'den gönderilen onay paketinin boyutu
