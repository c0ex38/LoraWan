from .utils import (
    calculate_time_on_air, calculate_bit_rate, calculate_energy_consumption, 
    calculate_path_loss, get_required_snr, get_sf_sensitivity,
    calculate_duty_cycle_off_time, get_mtu_limit, calculate_link_margin,
    calculate_noise_floor
)
import numpy as np

class SmartCitySimulation:
    def __init__(self, num_bins=100, area_size=10000, num_gateways=4, scenario='NORMAL'):
        self.num_bins = num_bins
        self.area_size = area_size
        self.scenario = scenario
        self.tx_power = 14 
        self.noise_floor = calculate_noise_floor()
        
        # Listeler
        self.device_types = []
        self.bin_sfs = []
        self.all_gw_stats = []
        self.best_gateways = []
        self.distances = []
        self.device_statuses = []
        self.failure_reasons = []
        
        self._initialize_gateways(num_gateways)
        self._apply_chaos_parameters()
        self._process_devices()
        self._populate_legacy_stats()

    def _initialize_gateways(self, num_gateways):
        offset = self.area_size / 4
        self.gateways = np.array([
            [offset, offset], [-offset, offset], 
            [offset, -offset], [-offset, -offset]
        ])[:num_gateways]

        if self.scenario == 'FAILURE' and len(self.gateways) > 1:
            self.gateways = self.gateways[1:]

    def _apply_chaos_parameters(self):
        self.is_chaos = (self.scenario == 'CHAOS')
        self.jammer_pos = np.array([1000, 1000]) if self.is_chaos else None

    def _calculate_device_signal(self, pos, d_type):
        gw_stats = {}
        best_snr = -float('inf')
        best_gw_idx = -1

        for g_idx, gw_pos in enumerate(self.gateways):
            d = np.linalg.norm(pos - gw_pos)
            indoor_loss = 20 if d_type == 'WATER' else (5 if d_type == 'BIN' else 0)
            
            pl = calculate_path_loss(d) + indoor_loss
            
            # Shadowing (Config'den çekiliyor)
            std = config.SHADOWING_STD_STORM if self.scenario == 'STORM' else config.SHADOWING_STD_NORMAL
            mean = -10 if self.scenario == 'STORM' else 0
            shadowing = np.random.normal(mean, std)
            
            # Fading & Jamming
            fading = np.random.uniform(-10, 5) if self.is_chaos else 0
            jamming = 0
            if self.is_chaos:
                if np.linalg.norm(pos - self.jammer_pos) < config.JAMMER_RADIUS:
                    jamming = config.JAMMER_POWER_DB
            
            rssi = self.tx_power - pl + shadowing + fading - jamming
            snr = rssi - self.noise_floor
            
            gw_stats[g_idx] = {
                'rssi': rssi, 'snr': snr, 'dist': d,
                'fading': fading, 'jamming': jamming
            }
            
            if snr > best_snr:
                best_snr = snr
                best_gw_idx = g_idx
                
        return gw_stats, best_snr, best_gw_idx

    def _process_devices(self):
        types = ['BIN', 'LIGHT', 'WATER', 'AIR']
        self.bin_positions = np.random.uniform(-self.area_size/2, self.area_size/2, (self.num_bins, 2))

        for i in range(self.num_bins):
            d_type = types[i % 4]
            self.device_types.append(d_type)
            pos = self.bin_positions[i]
            
            is_dead = self.is_chaos and np.random.random() < config.CHAOS_FAILURE_CHANCE
            gw_stats, best_snr, best_gw_idx = self._calculate_device_signal(pos, d_type)
            
            best_sf = 7
            status = 'ACTIVE'
            failure_reason = None

            if is_dead:
                status, failure_reason, best_sf = 'FAILED', 'DEAD', -1
            elif best_snr < get_required_snr(12):
                status, failure_reason, best_sf = 'FAILED', 'NO_LINK', -1
            else:
                for sf_val in range(7, 13):
                    if best_snr >= get_required_snr(sf_val) + 5:
                        best_sf = sf_val
                        break
                else:
                    best_sf = 12
            
            self.bin_sfs.append(best_sf)
            self.all_gw_stats.append(gw_stats)
            self.best_gateways.append(best_gw_idx)
            self.distances.append(gw_stats[best_gw_idx]['dist'] if best_gw_idx != -1 else 0)
            self.device_statuses.append(status)
            self.failure_reasons.append(failure_reason)

    def _populate_legacy_stats(self):
        self.bin_rssis = []
        self.bin_snrs = []
        for j in range(self.num_bins):
            bg = self.best_gateways[j]
            if bg != -1:
                self.bin_rssis.append(self.all_gw_stats[j][bg]['rssi'])
                self.bin_snrs.append(self.all_gw_stats[j][bg]['snr'])
            else:
                self.bin_rssis.append(-float('inf'))
                self.bin_snrs.append(-float('inf'))
            
    def run_analysis(self):
        results = []
        payload_size = 2 # Çöp doluluk oranı (1 byte) + cihaz id (1 byte)
        
        # Pil kapasitesi (mAh) - Tipik bir Li-ion pil 2500mAh
        battery_mah = 2500
        voltage = 3.3
        
        for i in range(self.num_bins):
            sf = self.bin_sfs[i]
            rssi = self.bin_rssis[i]
            snr = self.bin_snrs[i]
            d_type = self.device_types[i]
            
            toa = calculate_time_on_air(payload_size, sf)
            energy = calculate_energy_consumption(toa)
            
            total_battery_mj = battery_mah * voltage * 3600
            
            if d_type == 'LIGHT':
                transmissions_per_day = 144
            elif d_type == 'AIR':
                transmissions_per_day = 48
            elif d_type == 'WATER':
                transmissions_per_day = 1
            else:
                transmissions_per_day = 4
                
            daily_energy = energy * transmissions_per_day
            est_life_days = total_battery_mj / daily_energy if daily_energy > 0 else 0
            
            off_time = calculate_duty_cycle_off_time(toa)
            mtu = get_mtu_limit(sf)
            margin = calculate_link_margin(snr, sf)
            noise_floor = calculate_noise_floor()

            results.append({
                'id': i,
                'type': d_type,
                'status': self.device_statuses[i],
                'failure_reason': self.failure_reasons[i],
                'distance': self.distances[i],
                'sf': sf,
                'rssi': rssi,
                'snr': snr,
                'all_gw_stats': self.all_gw_stats[i],
                'link_margin': margin,
                'noise_floor': noise_floor,
                'gateway_id': self.best_gateways[i],
                'toa': toa,
                'off_time': off_time,
                'mtu_limit': mtu,
                'energy': energy,
                'bit_rate': calculate_bit_rate(sf),
                'battery_life': est_life_days / 365
            })
            
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
