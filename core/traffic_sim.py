import numpy as np
from . import config
from .utils import calculate_time_on_air, check_collision_sir

class TrafficSimulator:
    def __init__(self, simulation_results, duration_seconds=3600, num_channels=config.NUM_CHANNELS):
        self.devices = simulation_results
        self.duration = duration_seconds
        self.num_channels = num_channels
        self.packets = []
        
    def generate_traffic(self, interval_seconds=600, scenario='NORMAL'):
        """Zaman tabanlı paket trafiği üretir."""
        self.packets = []
        
        # SENARYO: Festival (FESTIVAL) - Yoğun trafik
        is_festival = (scenario == 'FESTIVAL')

        for dev in self.devices:
            # Faz 20: Eğer cihaz arızalıysa paket göndermez
            if dev.get('status') == 'FAILED':
                continue
                
            d_type = dev.get('type', 'BIN')
            
            # Cihaz Tipine Göre İletim Aralığı (Saniye)
            intervals = {'LIGHT': 600, 'AIR': 1800, 'WATER': 86400, 'BIN': interval_seconds}
            d_interval = intervals.get(d_type, interval_seconds)
            
            # Festival Modu Çarpanı
            if is_festival:
                d_interval = max(60, d_interval / 5)

            current_time = np.random.uniform(0, d_interval)
            toa_s = dev['toa'] / 1000
            
            while current_time < self.duration:
                self.packets.append({
                    'device_id': dev['id'],
                    'device_type': d_type,
                    'start_time': current_time,
                    'end_time': current_time + toa_s,
                    'sf': dev['sf'],
                    'rssi': dev['rssi'],
                    'channel_id': np.random.randint(0, self.num_channels),
                    'gateway_id': dev['gateway_id'],
                    'status': 'SUCCESS'
                })
                current_time += d_interval + np.random.uniform(-10, 10)
        
        self.packets.sort(key=lambda x: x['start_time'])
        return self.packets

    def run_collision_analysis(self):
        """Çakışma ve Gateway körlüğü analiz motoru."""
        # Sayaçlar ve Takip Yapıları
        stats = {
            'success': 0, 'collision': 0, 'blindness': 0,
            'co_sf_collisions': 0, 'cross_sf_collisions': 0
        }
        gw_busy_slots = {i: [] for i in range(config.MAX_GATEWAYS)} 
        
        # HIZLI ERİŞİM: Cihaz listesini bir map'e al (O(1) erişim için)
        device_map = {dev['id']: dev for dev in self.devices}
        
        # Cihaz bazlı başarı takibi
        device_stats = {dev['id']: {'total': 0, 'success': 0} for dev in self.devices}
        
        for i, p1 in enumerate(self.packets):
            dev_id = p1['device_id']
            device_stats[dev_id]['total'] += 1
            
            # Cihazın duyulabildiği tüm gateway'leri kontrol et
            p1_dev = device_map[dev_id]
            all_gw_stats = p1_dev['all_gw_stats']
            
            packet_received = False
            collision_type = None
            is_blind = False
            
            for gw_id_str, g_stat in all_gw_stats.items():
                gw_id = int(gw_id_str)
                if g_stat['rssi'] < config.MIN_RSSI_THRESHOLD: continue
                
                # Blindness Check
                is_blind = any(not (p1['end_time'] < b_s or p1['start_time'] > b_e) for b_s, b_e in gw_busy_slots[gw_id])
                if is_blind: continue

                # Collision Check
                collision = False
                # Forward search
                for j in range(i + 1, len(self.packets)):
                    p2 = self.packets[j]
                    if p2['start_time'] >= p1['end_time']: break
                    if p1['channel_id'] == p2['channel_id']:
                        p2_dev = device_map.get(p2['device_id'])
                        if p2_dev and str(gw_id) in p2_dev['all_gw_stats']:
                            if not check_collision_sir(p1['sf'], p2['sf'], g_stat['rssi'], p2_dev['all_gw_stats'][str(gw_id)]['rssi']):
                                collision = True
                                collision_type = 'CO_SF' if p1['sf'] == p2['sf'] else 'CROSS_SF'
                                break
                
                if collision: continue
                
                # Backward search
                for j in range(i - 1, -1, -1):
                    p2 = self.packets[j]
                    if p2['end_time'] <= p1['start_time']: break
                    if p1['channel_id'] == p2['channel_id']:
                        p2_dev = device_map.get(p2['device_id'])
                        if p2_dev and str(gw_id) in p2_dev['all_gw_stats']:
                            if not check_collision_sir(p1['sf'], p2['sf'], g_stat['rssi'], p2_dev['all_gw_stats'][str(gw_id)]['rssi']):
                                collision = True
                                collision_type = 'CO_SF' if p1['sf'] == p2['sf'] else 'CROSS_SF'
                                break
                
                if not collision:
                    # Bu gateway paketi başarıyla aldı! (Belki capture effect sayesinde, belki de temiz kanal)
                    packet_received = True
                    # Başarılı alım sonrası ACK penceresi için GW'yı meşgul et
                    ack_toa = calculate_time_on_air(config.ACK_PAYLOAD_BYTES, p1['sf']) / 1000
                    gw_busy_slots[gw_id].append((p1['end_time'] + 1.0, p1['end_time'] + 1.0 + ack_toa))
                    break
            
            if packet_received:
                p1['status'] = 'SUCCESS'
                stats['success'] += 1
                device_stats[dev_id]['success'] += 1
            else:
                p1['status'] = 'FAILED'
                if is_blind: 
                    stats['blindness'] += 1
                elif collision_type == 'CO_SF':
                    stats['co_sf_collisions'] += 1
                    stats['collision'] += 1
                elif collision_type == 'CROSS_SF':
                    stats['cross_sf_collisions'] += 1
                    stats['collision'] += 1
                else:
                    stats['collision'] += 1 # Genel çakışma

        # Cihaz listesine PDR ekle
        for dev in self.devices:
            ds = device_stats[dev['id']]
            dev['pdr'] = (ds['success'] / ds['total'] * 100) if ds['total'] > 0 else 100

        stats['total_packets'] = len(self.packets)
        stats['pdr'] = (stats['success'] / len(self.packets) * 100) if self.packets else 0
        return stats
