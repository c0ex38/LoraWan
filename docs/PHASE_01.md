# PHASE 01: Temel Koordinat Sistemi ve Alan Tanımı

## Hedef

Simülasyonun üzerinde koşacağı fiziksel alanın tanımlanması ve cihazların (node) bu alana yerleştirilmesi.

## Teknik Detay

- **Alan:** 10km x 10km (varsayılan) büyüklüğünde bir 2D düzlem.
- **Koordinat Sistemi:** Merkez (0,0) noktası olacak şekilde Kartezyen koordinat sistemi.
- **Dağılım:** `numpy.random.uniform` kullanılarak cihazların alan üzerine rastgele (stokastik) dağıtımı.

## Uygulama

`SmartCitySimulation` sınıfı başlatıldığında alanı tanımlar ve `bin_positions` dizisini oluşturur.

## LoRaWAN Bağlamı

Gerçek bir akıllı şehir kurulumunda cihaz yoğunluğu ve coğrafi dağılım, ağın kapasitesini ve ihtiyaç duyulan gateway sayısını belirleyen ilk kritik faktördür.
