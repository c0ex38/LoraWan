from utils import calculate_time_on_air, calculate_bit_rate, calculate_energy_consumption, calculate_path_loss, get_required_snr, get_sf_sensitivity
import numpy as np

class SmartCitySimulation:
    def __init__(self, num_bins=100, area_size=10000, num_gateways=4):
        self.num_bins = num_bins
        # Çoklu Gateway Yerleşimi (Kare şeklinde dağılım)
        offset = area_size / 4
        self.gateways = np.array([
            [offset, offset], [-offset, offset], 
            [offset, -offset], [-offset, -offset]
        ])[:num_gateways]
        
        self.bin_positions = np.random.uniform(-area_size/2, area_size/2, (num_bins, 2))
        
        # Faz 4: Sinyal ve GW Seçim Parametreleri
        self.tx_power = 14 
        self.noise_floor = -110 
        self.bin_sfs = []
        self.bin_rssis = []
        self.bin_snrs = []
        self.best_gateways = []
        self.distances = [] # En yakın GW mesafesi

        for pos in self.bin_positions:
            best_snr = -999
            best_rssi = -999
            best_sf = 12
            best_gw_idx = 0
            min_dist = 99999
            
            for gw_idx, gw_pos in enumerate(self.gateways):
                d = np.linalg.norm(pos - gw_pos)
                shadowing = np.random.normal(0, 6)
                pl = calculate_path_loss(d) + shadowing
                rssi = self.tx_power - pl
                snr = rssi - self.noise_floor
                
                # En iyi gateway'i seç (En yüksek SNR)
                if snr > best_snr:
                    best_snr = snr
                    best_rssi = rssi
                    best_gw_idx = gw_idx
                    min_dist = d
            
            # ADR: En iyi link için SF seç
            for sf in [7, 8, 9, 10, 11, 12]:
                if best_snr >= get_required_snr(sf) + 5:
                    best_sf = sf
                    break
            
            self.bin_sfs.append(best_sf)
            self.bin_rssis.append(best_rssi)
            self.bin_snrs.append(best_snr)
            self.best_gateways.append(best_gw_idx)
            self.distances.append(min_dist)
            
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
                'gateway_id': self.best_gateways[i],
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
