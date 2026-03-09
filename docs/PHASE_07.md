# PHASE 07: Kapsama Isı Haritası (Coverage Heatmap)

## Hedef

Şehir genelindeki kapsama boşluklarını (dead zones) görsel olarak tespit etmek.

## Teknik Detay

- **Grid Analizi:** Alan 100x100 piksellik bir grid'e bölündü.
- **Enterpolasyon:** Grid noktalarındaki tahmini sinyal seviyeleri hesaplanarak `pcolormesh` ile görselleştirildi.

## Uygulama

`visualizer.py` içine `plot_coverage_heatmap` fonksiyonu eklendi.

## LoRaWAN Bağlamı

Ağ planlama ekipleri, bu haritalara bakarak gateway konumlarını optimize eder ve sinyal kalitesinin düşük olduğu "kör noktaları" belirler.
