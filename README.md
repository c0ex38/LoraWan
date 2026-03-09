# 📡 LoRaWAN Spreading Factor & Network Capacity Simulator

Bu proje, Akıllı Şehir senaryolarında (örneğin 1000+ akıllı çöp kutusu) LoRaWAN ağ performansını analiz etmek için geliştirilmiş profesyonel bir **Discrete Event Simulation** framework'üdür.

## 🌟 Öne Çıkan Özellikler

- **Gelişmiş Radyo Modeli:** Log-Distance Path Loss ve rastgele **Shadowing (6dB)** etkileri ile gerçekçi şehir ortamı.
- **Dinamik ADR (Adaptive Data Rate):** Cihazların sinyal kalitesine (SNR) göre en uygun SF7-SF12 değerini otomatik seçmesi.
- **Çoklu Gateway (Macro-Diversity):** Şehre dağıtılmış 4 kule üzerinden kapsama alanı analizi.
- **Frekans Atlamalı İletişim:** 8 farklı frekans kanalında trafik simülasyonu.
- **Downlink & Half-Duplex Analizi:** Gateway'lerin onay (ACK) gönderirken yaşadığı "körlük" (blindness) etkisinin modellenmesi.
- **İnteraktif Dashboard:** Tüm sonuçların statik görseller yerine modern bir HTML arayüzünde sunulması.

## 📂 Proje Yapısı

- `main.py`: Simülasyonu başlatan ana kontrol merkezi.
- `simulation.py`: Şehir mimarisi, cihaz yerleşimi ve ADR mantığı.
- `traffic_sim.py`: Zaman tabanlı paket trafiği ve çakışma (collision/blindness) motoru.
- `utils.py`: Matematiksel modeller (ToA, Path Loss, SIR, Energy).
- `visualizer.py`: Profesyonel grafik ve harita üretimi.
- `html/`: Modern, karanlık mod destekli interaktif analiz dashboard'u.
- `images/`: Üretilen tüm analiz sonuçlarının toplandığı görsel depo.

## 🚀 Hızlı Başlangıç

### 1. Simülasyonu Çalıştırın

Bu komut 1000 cihazlık profesyonel senaryoyu koşturur ve tüm grafikleri üretir:

```bash
python3 main.py
```

### 2. Dashboard'u Başlatın

Arayüzü görüntülemek için yerel sunucuyu açın:

```bash
python3 -m http.server 8000
```

Ardından tarayıcınızdan şu adrese gidin:
🔗 **[http://localhost:8000/html/index.html](http://localhost:8000/html/index.html)**

## 📊 Analiz Ekran Görüntüleri

### Çoklu Gateway ve SF Dağılımı

![City Map](images/city_map_sf_distribution.png)

### Ağ Ölçeklenebilirliği ve Kayıp Analizi

![PDR Analysis](images/network_pdr_analysis.png)

## � Teknik Rapor

Simülasyonun bilimsel detayları, kullanılan formüller ve 2000 cihaza kadar yapılan stres testi sonuçları için `project_report.md` dosyasını inceleyebilirsiniz.

---

_Bu proje LoRaWAN ağlarının planlanması ve optimizasyonu için bilimsel bir temel sunar._
