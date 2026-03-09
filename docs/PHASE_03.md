# PHASE 03: Cihaz Tipleri ve Hiyerarşi

## Hedef

Simülasyona gerçekçi cihaz profilleri ekleyerek heterojen bir ağ yapısı kurmak.

## Teknik Detay

- **Profiller:**
  - `BIN` (Akıllı Çöp Kutusu)
  - `LIGHT` (Akıllı Aydınlatma)
  - `WATER` (Su Sayacı)
  - `AIR` (Hava Kalite Sensörü)
- **Fiziksel Özellikler:** Su sayaçları gibi yeraltında veya kapalı alanda bulunan cihazlar için ek "Indoor Loss" (İç Mekan Kaybı) eklendi.

## Uygulama

`simulation.py` içinde cihazlara tip ataması yapıldı ve sinyal hesaplamalarına `indoor_loss` (20dB su sayaçları için) parametresi eklendi.

## LoRaWAN Bağlamı

LoRaWAN kullanım senaryoları çeşitlidir. Derin iç mekan kapsama ihtiyacı (Deep Indoor Coverage), LoRa'nın en güçlü olduğu alanlardan biridir.
