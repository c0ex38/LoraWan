# PHASE 19: Inter-SF Girişimi ve Capture Effect

## Hedef

Fiziksel katman çakışmalarının karmaşık yapısını (SIR tabanlı) modellemek.

## Teknik Detay

- **SIR (Signal-to-Interference Ratio):** İki sinyal arasındaki güç farkı.
- **Capture Effect:** LoRa'da girişi yapan sinyalin 6dB daha güçlü olması halinde asıl paketin kurtarılması kuralı.
- **Rejection Matrix:** Farklı SF'lerin birbirine girişimi (Cross-SF).

## Uygulama

`check_collision_sir` fonksiyonu ve `plot_spectral_efficiency` grafiği eklendi.

## LoRaWAN Bağlamı

Gerçek dünya senaryolarında çakışma her zaman kayıp demek değildir; güçlü olan sinyal "yakalanabilir". Bu, ağ kapasitesini matematiksel olarak artırır.
