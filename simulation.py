import numpy as np
import matplotlib.pyplot as plt
from utils import calculate_time_on_air, calculate_bit_rate, calculate_energy_consumption

class SmartCitySimulation:
    def __init__(self, num_bins=20, area_size=5000):
        """
        num_bins: Çöp kutusu sayısı
        area_size: Şehir alanı (metre, gateway merkezde)
        """
        self.num_bins = num_bins
        self.area_size = area_size
        self.gateway_pos = (0, 0)
        
        # Çöp kutularını rastgele yerleştir
        self.bin_positions = np.random.uniform(-area_size/2, area_size/2, (num_bins, 2))
        self.distances = np.linalg.norm(self.bin_positions - self.gateway_pos, axis=1)
        
        # Mesafeye göre SF ata (Basit bir model: mesafe arttıkça SF artar)
        # 0-1km: SF7, 1-2km: SF8, 2-3km: SF9, 3-4km: SF10, 4-5km: SF11, 5km+: SF12
        self.bin_sfs = []
        for d in self.distances:
            if d < 1000: sf = 7
            elif d < 2000: sf = 8
            elif d < 3000: sf = 9
            elif d < 4000: sf = 10
            elif d < 5000: sf = 11
            else: sf = 12
            self.bin_sfs.append(sf)
            
    def run_analysis(self):
        results = []
        payload_size = 2 # Çöp doluluk oranı (1 byte) + cihaz id (1 byte)
        
        # Pil kapasitesi (mAh) - Tipik bir Li-ion pil 2500mAh
        battery_mah = 2500
        voltage = 3.3
        
        print(f"{'Bin ID':<10} | {'SF':<5} | {'ToA (ms)':<10} | {'Energy (mJ)':<15} | {'Est. Life (Days)'}")
        print("-" * 75)
        
        for i in range(self.num_bins):
            sf = self.bin_sfs[i]
            toa = calculate_time_on_air(payload_size, sf)
            energy = calculate_energy_consumption(toa)
            
            # Basit bir pil ömrü hesabı: Günde 4 kez veri gönderdiğini varsayalım
            # Toplam enerji (mWh) = 2500mAh * 3.3V = 8250 mWh = 29700 Joule = 29,700,000 mJ
            total_battery_mj = battery_mah * voltage * 3600 # mAh to mJ
            transmissions_per_day = 4
            daily_energy = energy * transmissions_per_day
            
            # Bekleme akımını (sleep current) şimdilik ihmal ediyoruz veya ekleyebiliriz (~2uA)
            est_life_days = total_battery_mj / daily_energy if daily_energy > 0 else 0
            
            results.append({
                'id': i,
                'distance': self.distances[i],
                'sf': sf,
                'toa': toa,
                'energy': energy,
                'bit_rate': calculate_bit_rate(sf),
                'battery_life': est_life_days / 365 # Yıl cinsinden
            })
            
            print(f"{i:<10} | {sf:<5} | {toa:<10.2f} | {energy:<15.2f} | {est_life_days:<10.0f}")
            
        return results

if __name__ == "__main__":
    sim = SmartCitySimulation(num_bins=15)
    results = sim.run_analysis()
