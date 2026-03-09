# PHASE 06: Spreading Factor (SF) Dağılımı ve ADR

## Hedef

Cihazların sinyal kalitesine göre en verimli yayılma faktörünü (SF7 - SF12) seçmesini sağlamak.

## Teknik Detay

- **Eşik Değerleri:**
  - SF7: > -125 dBm (Sensitivity)
  - SF12: > -140 dBm (Sensitivity)
- **Mantık:** Sinyal güçlendikçe daha düşük SF (daha hızlı veri, daha az enerji), sinyal zayıfladıkça daha yüksek SF seçilir.

## Uygulama

`simulation.py` içine `get_required_snr` tabanlı bir seçim mantığı eklendi.

## LoRaWAN Bağlamı

ADR (Adaptive Data Rate), LoRaWAN'ın pil ömrünü maksimize eden en kritik algoritmasıdır. Cihazlar gereksiz yere yüksek güç kullanmazlar.
