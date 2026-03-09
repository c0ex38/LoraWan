# PHASE 15: Akademik Kısıtlar: Duty Cycle ve MTU

## Hedef

Simülasyonun LoRaWAN yasal ve teknik limitlerine tam uyumunu sağlamak.

## Teknik Detay

- **Duty Cycle:** %1 kuralı (Avrupa 868MHz bandı). Bir cihaz konuştuğu sürenin 99 katı kadar sessiz kalmalıdır ($T_{off}$).
- **MTU (Maximum Transmission Unit):** SF arttıkça izin verilen veri paket boyutunun düşürülmesi.

## Uygulama

`calculate_duty_cycle_off_time` ve `get_mtu_limit` fonksiyonları ile kurallar dijitalleştirildi.

## LoRaWAN Bağlamı

Bu kurallara uyulmaması ağın regülasyon dışı kalmasına ve diğer kablosuz sistemlere zarar vermesine neden olur.
