# PHASE 04: Sinyal Gücü (RSSI) ve SNR Hesaplama

## Hedef

Alıcı tarafındaki sinyal kalitesini belirleyen temel metriklerin hesaplanması.

## Teknik Detay

- **RSSI (Received Signal Strength Indicator):** $TX_{Power} - PathLoss + Shadowing$
- **SNR (Signal-to-Noise Ratio):** $RSSI - NoiseFloor$
- **Noise Floor:** Tipik olarak LoRaWAN için -120 dBm civarı (125kHz bant genişliğinde).

## Uygulama

Cihazların her biri için gateway tarafındaki RSSI ve SNR değerleri dinamik olarak hesaplanarak `results` listesine eklendi.

## LoRaWAN Bağlamı

LoRa, gürültü seviyesinin altında (negatif SNR) bile çalışabilen nadir teknolojilerdendir. Bu faz, bu özelliğin analitik temelini atmıştır.
