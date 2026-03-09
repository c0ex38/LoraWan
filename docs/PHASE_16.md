# PHASE 16: Link Margin (Bağlantı Payı) Analizi

## Hedef

Bir bağlantının ne kadar güvenli (kopmaya ne kadar yakın) olduğunu ölçmek.

## Teknik Detay

- **Margin:** Mevcut SNR ile o SF için gereken minimum SNR arasındaki fark.
- **Hesaplama:** $Margin = SNR_{Actual} - SNR_{Required}$

## Uygulama

`calculate_link_margin` fonksiyonu eklendi ve dashboard'da görselleştirildi.

## LoRaWAN Bağlamı

Yüksek Link Margin, ağın yağmur veya fırtına gibi hava değişimlerine karşı ne kadar dayanıklı olduğunun (Robustness) bir göstergesidir.
