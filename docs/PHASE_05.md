# PHASE 05: Çoklu Gateway Mimarisini Destekleme

## Hedef

Simülasyonu tekil bir merkezden çıkarıp gerçekçi bir hücresel ağ yapısına taşımak.

## Teknik Detay

- **Yerleşim:** Gateway'ler alan üzerine stratejik noktalara (dört köşe) yerleştirildi.
- **Seçim:** Cihazların en yüksek SNR değerine sahip gateway'e bağlanması sağlandı.

## Uygulama

`self.gateways` dizisi oluşturuldu ve her cihaz için en yakın/en güçlü gateway tespiti döngüsel olarak yapıldı.

## LoRaWAN Bağlamı

LoRaWAN, geleneksel hücresel ağlardan farklı olarak bir "yıldız tipi yıldız" (star-of-stars) mimarisine sahiptir. Bir paket birden fazla gateway tarafından duyulabilir; bu da ağın kapasitesini artırır.
