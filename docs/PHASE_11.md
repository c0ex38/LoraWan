# PHASE 11: Enerji Tüketimi ve Pil Ömrü Tahmini

## Hedef

Cihazların saha ömürlerini belirleyen enerji profilini matematiksel olarak modellemek.

## Teknik Detay

- **Enerji Modeli:** $E = V \cdot I \cdot t$
- **Parametreler:**
  - TX Akımı: ~120mA (max güçte)
  - Uyku Akımı: ~2uA
  - Voltaj: 3.3V
- **Hesaplama:** ToA (Time on Air) ve iletim sıklığı bazlı günlük tüketim.

## Uygulama

`core/utils.py` içindeki `calculate_energy_consumption` fonksiyonu bu modeli uygular.

## LoRaWAN Bağlamı

LoRaWAN'ın en büyük vaadi "10 yıl pil ömrü"dür. Bu faz, bu vaadin hangi şartlarda (düşük SF, az veri) gerçekçi olduğunu ispatlar.
