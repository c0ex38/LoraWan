from utils import calculate_time_on_air, calculate_bit_rate, calculate_energy_consumption, calculate_path_loss, get_required_snr, get_sf_sensitivity
import numpy as np

class SmartCitySimulation:
    def __init__(self, num_bins=20, area_size=5000):
        self.num_bins = num_bins
        self.gateway_pos = (0, 0)
        self.bin_positions = np.random.uniform(-area_size/2, area_size/2, (num_bins, 2))
        self.distances = np.linalg.norm(self.bin_positions - self.gateway_pos, axis=1)
        
        # Faz 2: Sinyal Parametreleri
        self.tx_power = 14 # dBm (Yasal limit)
        self.noise_floor = -110 # dBm
        self.bin_sfs = []
        self.bin_rssis = []
        self.bin_snrs = []
        
        for d in self.distances:
            # 1. Path Loss + Shadowing (rastgele bina/engel etkisi)
            shadowing = np.random.normal(0, 6) # 6dB standart sapma
            pl = calculate_path_loss(d) + shadowing
            
            # 2. RSSI ve SNR Hesapla
            rssi = self.tx_power - pl
            snr = rssi - self.noise_floor
            
            self.bin_rssis.append(rssi)
            self.bin_snrs.append(snr)
            
            # 3. ADR: Bu sinyal kalitesi için en iyi (en düşük) SF'yi seç
            best_sf = 12 # Default en güvenli
            for sf in [7, 8, 9, 10, 11, 12]:
                required_snr = get_required_snr(sf)
                if snr >= required_snr + 5: # 5dB güvenlik marjı
                    best_sf = sf
                    break
            self.bin_sfs.append(best_sf)
            
    def run_analysis(self):
        results = []
        payload_size = 2 # Çöp doluluk oranı (1 byte) + cihaz id (1 byte)
        
        # Pil kapasitesi (mAh) - Tipik bir Li-ion pil 2500mAh
        battery_mah = 2500
        voltage = 3.3
        
        print(f"{'Bin ID':<10} | {'SF':<5} | {'RSSI (dBm)':<12} | {'SNR (dB)':<10} | {'Energy (mJ)':<15}")
        print("-" * 75)
        
        for i in range(self.num_bins):
            sf = self.bin_sfs[i]
            rssi = self.bin_rssis[i]
            snr = self.bin_snrs[i]
            toa = calculate_time_on_air(payload_size, sf)
            energy = calculate_energy_consumption(toa)
            
            # ... pil ömrü hesapları aynı ...
            total_battery_mj = battery_mah * voltage * 3600
            transmissions_per_day = 4
            daily_energy = energy * transmissions_per_day
            est_life_days = total_battery_mj / daily_energy if daily_energy > 0 else 0
            
            results.append({
                'id': i,
                'distance': self.distances[i],
                'sf': sf,
                'rssi': rssi,
                'snr': snr,
                'toa': toa,
                'energy': energy,
                'bit_rate': calculate_bit_rate(sf),
                'battery_life': est_life_days / 365
            })
            
            print(f"{i:<10} | {sf:<5} | {rssi:<12.1f} | {snr:<10.1f} | {energy:<15.2f}")
            
        return results

if __name__ == "__main__":
    sim = SmartCitySimulation(num_bins=15)
    results = sim.run_analysis()
