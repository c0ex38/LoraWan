from .utils import (
    calculate_time_on_air, calculate_bit_rate, calculate_energy_consumption, 
    calculate_path_loss, get_required_snr, get_sf_sensitivity,
    calculate_duty_cycle_off_time, get_mtu_limit, calculate_link_margin
)
import numpy as np

class SmartCitySimulation:
    def __init__(self, num_bins=100, area_size=10000, num_gateways=4, scenario='NORMAL'):
        self.num_bins = num_bins
        self.area_size = area_size
        self.scenario = scenario
        # Çoklu Gateway Yerleşimi (Kare şeklinde dağılım)
        offset = area_size / 4
        self.gateways = np.array([
            [offset, offset], [-offset, offset], 
            [offset, -offset], [-offset, -offset]
        ])[:num_gateways]

        # SENARYO: Gateway Arızası (FAILURE)
        if scenario == 'FAILURE' and len(self.gateways) > 1:
            self.gateways = self.gateways[1:] # İlk gateway arızalı (GW0 devre dışı)
        
        self.bin_positions = np.random.uniform(-area_size/2, area_size/2, (num_bins, 2))
        
        # Faz 4: Sinyal ve GW Seçim Parametreleri
        self.tx_power = 14 
        self.noise_floor = -110 
        self.device_types = [] # 'BIN', 'LIGHT', 'WATER', 'AIR'
        self.bin_sfs = []
        self.bin_rssis = []
        self.bin_snrs = []
        self.best_gateways = []
        self.distances = [] 

        types = ['BIN', 'LIGHT', 'WATER', 'AIR']
        
        for i, pos in enumerate(self.bin_positions):
            # Cihaz Tipi Ata
            d_type = types[i % 4]
            self.device_types.append(d_type)
            
            # Cihaz Tipine Göre Ek Kayıplar (Penetrasyon)
            indoor_loss = 0
            if d_type == 'WATER': # Su sayaçları bodrumda
                indoor_loss = 20
            elif d_type == 'BIN':
                indoor_loss = 5 # Metal kutu etkisi
            
            best_snr = -999
            best_rssi = -999
            best_sf = 12
            best_gw_idx = 0
            min_dist = 99999
            
            for gw_idx, gw_pos in enumerate(self.gateways):
                d = np.linalg.norm(pos - gw_pos)
                shadowing_std = 6
                if self.scenario == 'STORM':
                    shadowing_std = 12
                    shadowing = np.random.normal(-10, shadowing_std)
                else:
                    shadowing = np.random.normal(0, shadowing_std)
                
                pl = calculate_path_loss(d) + shadowing + indoor_loss
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
            d_type = self.device_types[i]
            
            toa = calculate_time_on_air(payload_size, sf)
            energy = calculate_energy_consumption(toa)
            
            total_battery_mj = battery_mah * voltage * 3600
            
            # Cihaz Tipine Göre Veri Gönderim Sıklığı
            if d_type == 'LIGHT':
                transmissions_per_day = 144 # 10 dakikada bir
            elif d_type == 'AIR':
                transmissions_per_day = 48 # 30 dakikada bir
            elif d_type == 'WATER':
                transmissions_per_day = 1 # Günde 1 kez
            else: # BIN
                transmissions_per_day = 4 # 6 saatte bir
                
            daily_energy = energy * transmissions_per_day
            est_life_days = total_battery_mj / daily_energy if daily_energy > 0 else 0
            
            # FAZ 15: Duty Cycle ve MTU
            off_time = calculate_duty_cycle_off_time(toa)
            mtu = get_mtu_limit(sf)
            
            # FAZ 16: Link Margin
            margin = calculate_link_margin(snr, sf)

            results.append({
                'id': i,
                'type': d_type,
                'distance': self.distances[i],
                'sf': sf,
                'rssi': rssi,
                'snr': snr,
                'link_margin': margin,
                'gateway_id': self.best_gateways[i],
                'toa': toa,
                'off_time': off_time,
                'mtu_limit': mtu,
                'energy': energy,
                'bit_rate': calculate_bit_rate(sf),
                'battery_life': est_life_days / 365
            })
            
            print(f"{d_type:<10} | {sf:<5} | {rssi:<12.1f} | {snr:<10.1f} | {energy:<15.2f}")
            
        return results

    def optimize_gateway_placement(self):
        """
        AI Planlama: Mevcut ağdaki zayıf noktaları analiz eder ve 
        toplam SNR kazancını maksimize edecek en iyi yeni Gateway konumunu önerir.
        """
        grid_points = 10 # 10x10 tarama (Akademik hassasiyet)
        half_size = self.area_size / 2
        x_coords = np.linspace(-half_size, half_size, grid_points)
        y_coords = np.linspace(-half_size, half_size, grid_points)
        
        best_gain = -1
        best_coord = (0, 0)
        current_avg_snr = np.mean(self.bin_snrs) if self.bin_snrs else 0
        
        for tx in x_coords:
            for ty in y_coords:
                new_gw = np.array([tx, ty])
                total_new_snr = 0
                
                for i, pos in enumerate(self.bin_positions):
                    # Bu cihaz için yeni GW daha mı iyi sonuç veriyor?
                    d = np.linalg.norm(pos - new_gw)
                    d_type = self.device_types[i]
                    indoor_loss = 20 if d_type == 'WATER' else (5 if d_type == 'BIN' else 0)
                    
                    pl = calculate_path_loss(d) + indoor_loss
                    rssi = self.tx_power - pl
                    snr = rssi - self.noise_floor
                    
                    # Mevcut en iyi SNR ile kıyasla
                    effective_snr = max(snr, self.bin_snrs[i])
                    total_new_snr += effective_snr
                
                avg_new_snr = total_new_snr / self.num_bins
                gain = avg_new_snr - current_avg_snr
                
                if gain > best_gain:
                    best_gain = gain
                    best_coord = (tx, ty)
        
        return {
            'best_coord': [float(best_coord[0]), float(best_coord[1])],
            'snr_gain': round(best_gain, 2),
            'recommended': True
        }

if __name__ == "__main__":
    sim = SmartCitySimulation(num_bins=15)
    results = sim.run_analysis()
