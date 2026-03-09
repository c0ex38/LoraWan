# PHASE 14: Time on Air (ToA) Hesaplamaları

## Hedef

Bir paketin havada ne kadar süre kaldığını (iletim süresi) hassas şekilde hesaplamak.

## Teknik Detay

- **Değişkenler:** Payload boyutu, SF, Bant Genişliği (125kHz), CR (Coding Rate), Header durumu.
- **Formül:** Sembol süresi ($T_s$) üzerinden fiziksel katman parametrelerinin toplamı.

## Uygulama

`utils.py` içindeki `calculate_time_on_air` fonksiyonu, LoRa PHY spesifikasyonlarına göre güncellendi.

## LoRaWAN Bağlamı

ToA, hem enerji tüketimini hem de ağın çakışma olasılığını doğrudan etkileyen en temel "hava süresi" metriğidir.
