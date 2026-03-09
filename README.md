# 📡 LoRaWAN Digital Twin: Spreading Factor & Network Capacity Simulator

Bu proje, LoRaWAN ağlarının fiziksel katman (PHY) ve MAC katmanı davranışlarını bir Akıllı Şehir senaryosu üzerinden simüle eden 20 aşamalı, kapsamlı bir analiz ve araştırma aracıdır.

## 🚀 Proje Evrimi: 20 Fazlık Teknik Maraton

Bu simülatör, basit bir radyo modelinden başlayarak sektör standartlarında bir **Digital Twin** (Dijital İkiz) haline getirilmiştir. Tüm gelişim sürecini ve teknik ispatları [Teknik Dokümantasyon Dizini](docs/README.md) üzerinden inceleyebilirsiniz.

### 🌟 Önemli Kilometre Taşları

- **Faz 1-5:** Temel koordinat sistemi, Path Loss modelleri ve çoklu Gateway mimarisi.
- **Faz 6-10:** ADR (Adaptive Data Rate) algoritmaları ve mekansal haritalama (Heatmap).
- **Faz 11-15:** Enerji tüketimi modelleme, yasal kısıtlar (Duty Cycle) ve MTU limitleri.
- **Faz 16-20:** **Kaos Mühendisliği**, Link Margin analizi, **Macro-Diversity** (Yedeklilik), **Inter-SF Interference** ve $O(N \log N)$ performans optimizasyonu.

## 🧐 Öne Çıkan İleri Seviye Özellikler

- **Kaos Simülasyonu (Phase 20):** Donanım arızaları, aktif Jamming (sinyal karıştırma) ve derin sönümlenme (fading) etkilerinin modellenmesi.
- **Makro-Çeşitlilik (Phase 18):** Bir paketin birden fazla gateway tarafından duyulabilmesi (Redundancy) üzerinden ağ güvenilirliği artırımı.
- **Inter-SF & Capture Effect (Phase 19):** Farklı SF'lerin birbiriyle girişimi ve güçlü sinyalin çakışmadan kurtulabilme (SIR tabanlı) analizi.
- **Yüksek Performans:** Binlerce cihazlık trafik analizlerini saniyeler içinde tamamlayan optimize edilmiş çakışma motoru.

## 📂 Proje Yapısı

- `core/simulation.py`: Şehir mimarisi, cihaz yerleşimi ve kaos senaryoları.
- `core/traffic_sim.py`: $O(N \log N)$ hızında optimize edilmiş trafik ve çakışma motoru.
- `core/utils.py`: Fiziksel katman modelleri (ToA, SIR, Energy, Path Loss).
- `core/visualizer.py`: 12+ farklı teknik analiz grafiği üreten görselleştirme motoru.
- `web/`: Modern Dashboard (Flask tabanlı, SSE destekli gerçek zamanlı log akışı).
- `docs/`: 20 fazın her biri için teknik raporlar.
- `assets/plots/`: Üretilen güncel analiz görselleri.

## �️ Kurulum ve Çalıştırma

### 1. Gereksinimler

```bash
pip install flask flask-cors numpy matplotlib scipy
```

### 2. Uygulamayı Başlatın

Dashboard sunucusunu başlatmak için:

```bash
python3 web/app.py
```

Ardından tarayıcınızdan **[http://localhost:8000](http://localhost:8000)** adresine gidin.

## 📊 Analiz Ekran Görüntüleri

### Ağ Yedeklilik ve Kaos Analizi

![Reliability Map](assets/plots/reliability_heatmap.png)

### Sinyal Kalitesi (RSSI/SNR)

![Signal Quality](assets/plots/signal_quality.png)

### Kapsama Isı Haritası

![Heatmap](assets/plots/coverage_heatmap.png)

---

_Bu dokümantasyon ve simülasyon, projenin akademik ve mühendislik ispatlarını kayıt altına almak için oluşturulmuştur._
