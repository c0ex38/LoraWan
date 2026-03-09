# PHASE 09: Cihaz Tipi Performans Analizi

## Hedef

Farklı kullanım senaryolarındaki cihazların (su sayacı vs. hava sensörü) başarı oranlarını kıyaslamak.

## Teknik Detay

- **Gruplama:** Cihaz tiplerine göre PDR (Packet Delivery Ratio) ve enerji tüketimi ortalamaları.
- **Farklılaşma:** Tipik bir su sayacı (derin iç mekan) ile bir hava sensörünün (açık alan) performans uçurumu.

## Uygulama

`plot_device_type_stats` fonksiyonu ile kategorik analizler eklendi.

## LoRaWAN Bağlamı

Uygulama bazlı SLA (Service Level Agreement) takibi için cihaz tipi bazlı raporlama şarttır.
