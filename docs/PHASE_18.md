# PHASE 18: Gateway Diversity (Yedeklilik) Analizi

## Hedef

Ağın yedeklilik kapasitesini ve makro-çeşitlilik (Macro-Diversity) avantajını ölçmek.

## Teknik Detay

- **Yedeklilik Katsayısı:** Bir cihazın aynı anda kaç farklı gateway tarafından duyulabildiği.
- **Seçim:** En güçlü sinyal üzerinden değil, herhangi bir gateway tarafından alınması halinde başarılı sayılması.

## Uygulama

`plot_gateway_redundancy` fonksiyonu ve `run_collision_analysis` içinde çoklu alım mantığı uygulandı.

## LoRaWAN Bağlamı

Gateway yedekliliği, paket kaybını %50'ye kadar azaltabilen profesyonel bir ağ tasarımı stratejisidir.
