# PHASE 13: Dinamik Trafik ve Çakışma Analizi (Initial)

## Hedef

Ağdaki paketlerin zaman ekseninde birbirini etkilemesini simüle etmek.

## Teknik Detay

- **Trafik Üretimi:** Poisson dağılımına benzer rastgele paket başlangıç zamanları.
- **Çakışma Şartı:** İki paketin aynı anda, aynı kanalda ve aynı gateway'de olması.

## Uygulama

`TrafficSimulator` sınıfı ve `generate_traffic` fonksiyonu ile ilk çatışma senaryoları kurgulandı.

## LoRaWAN Bağlamı

LoRaWAN, ALOHA tabanlı bir erişim yöntemi kullanır. Cihazlar kanalı dinlemeden konuşur; bu da ağ yoğunlaştıkça çakışmaların kaçınılmaz olduğu anlamına gelir.
