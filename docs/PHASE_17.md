# PHASE 17: Gürültü Altı İletişim (Sub-Noise Recovery)

## Hedef

LoRa'nın gürültü seviyesinin altından veri çekebilme yeteneğini görselleştirmek.

## Teknik Detay

- **Konsept:** Negatif SNR değerlerinde bile başarılı veri alımı.
- **Gürültü Tabanı:** Termal gürültü hesaplaması.

## Uygulama

`plot_signal_vs_noise` fonksiyonu ile gürültü çizgisinin altındaki başarılı paketler ispatlandı.

## LoRaWAN Bağlamı

LoRa'yı diğer LPWAN teknolojilerinden (Sigfox, NB-IoT vb.) ayıran en büyük fark, CSS (Chirp Spread Spectrum) modülasyonu sayesinde gürültü altında çalışabilmesidir.
