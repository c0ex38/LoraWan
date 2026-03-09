# PHASE 12: Mahalle Bazlı Performans İstatistikleri

## Hedef

Ağ performansını sadece global değil, yerel (mekansal) bazda analiz etmek.

## Teknik Detay

- **Kümeleme:** Alanın sanal mahalle bölümlerine (Kuzey, Güney, Merkez vb.) ayrılması.
- **Metrik:** Her mahalle için ayrı PDR (Packet Delivery Ratio) hesaplaması.

## Uygulama

`visualizer.py` içine `plot_neighborhood_stats` fonksiyonu eklendi.

## LoRaWAN Bağlamı

Gerçek şehir operasyonlarında, binaların yoğun olduğu bir mahalle ile parkların olduğu bir mahallenin kapsama kalitesi farklılık gösterir. Bu analiz yerel iyileştirme kararları için kritiktir.
