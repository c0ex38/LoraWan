# PHASE 02: Path Loss (Yol Kaybı) Modelleme

## Hedef

Radyo sinyallerinin mesafe ile nasıl zayıfladığını matematiksel olarak modellemek.

## Teknik Detay

- **Model:** Log-Distance Path Loss Model.
- **Formül:** $PL = PL_0 + 10 \cdot n \cdot \log_{10}(d/d_0)$
- **Parametreler:**
  - $n$ (Path Loss Exponent): Şehir içi ortam için 3.0 ile 4.0 arası.
  - $PL_0$: 1 metredeki referans kayıp.

## Uygulama

`core/utils.py` içindeki `calculate_path_loss` fonksiyonu bu modeli kullanarak mesafeye bağlı kayıp değerini dB cinsinden döndürür.

## LoRaWAN Bağlamı

LoRa, yüksek hassasiyeti sayesinde çok yüksek yol kayıplarında (-148 dBm'e kadar) bile veri alabilir. Bu model, kapsama alanı tahminlerinin temelidir.
