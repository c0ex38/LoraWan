import numpy as np
from .utils import calculate_time_on_air, check_collision_sir

class TrafficSimulator:
    def __init__(self, simulation_results, duration_seconds=3600, num_channels=8):
        self.devices = simulation_results
        self.duration = duration_seconds
        self.num_channels = num_channels
        self.packets = []
        
    def generate_traffic(self, interval_seconds=600, scenario='NORMAL'):
        self.packets = []
        
        # SENARYO: Festival (FESTIVAL) - Yoğun trafik
        is_festival = scenario == 'FESTIVAL'

        for dev in self.devices:
            d_type = dev.get('type', 'BIN')
            
            # Cihaz Tipine Göre Interval (Saniye)
            if d_type == 'LIGHT':
                d_interval = 600 # 10 dk
            elif d_type == 'AIR':
                d_interval = 1800 # 30 dk
            elif d_type == 'WATER':
                d_interval = 86400 # 24 saat (Günde 1)
            else: # BIN
                d_interval = interval_seconds # Varsayılan (Genelde 600)
            
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
        """
        Zaman ekseninde çakışmaları ve Gateway körlüğünü (Half-Duplex) kontrol eder.
        """
        # Sayaçlar ve Takip Yapıları
        success_count = 0
        collision_count = 0
        blindness_count = 0
        co_sf_collisions = 0
        cross_sf_collisions = 0
        gw_busy_slots = {i: [] for i in range(20)} # Max 20 GW desteği
        
        # Cihaz bazlı başarı takibi
        device_stats = {dev['id']: {'total': 0, 'success': 0} for dev in self.devices}
        
        for i, p1 in enumerate(self.packets):
            dev_id = p1['device_id']
            device_stats[dev_id]['total'] += 1
            
            # Cihazın duyulabildiği tüm gateway'leri kontrol et (Macro-Diversity)
            all_gw_stats = next(d['all_gw_stats'] for d in self.devices if d['id'] == dev_id)
            
            packet_received_by_any_gw = False
            
            # Bu paket için hata nedenlerini takip et (Görselleştirme için p1'e eklenebilir)
            p1_collision_type = None
            
            for gw_id_str, stats in all_gw_stats.items():
                gw_id = int(gw_id_str)
                # RSSI çok düşükse bu gateway zaten duyamaz (-130 dBm altı)
                if stats['rssi'] < -130: continue
                
                # 1. Gateway Körlüğü Kontrolü (Bu spesifik GW için)
                is_blind = False
                for busy_start, busy_end in gw_busy_slots[gw_id]:
                    if not (p1['end_time'] < busy_start or p1['start_time'] > busy_end):
                        is_blind = True
                        break
                
                if is_blind: continue

                # 2. Çakışma Kontrolü (Bu spesifik GW ve Kanal için)
                collision = False
                for j, p2 in enumerate(self.packets):
                    if i == j: continue
                    # Aynı gateway ve aynı kanalda çakışma riski
                    overlap = not (p1['end_time'] < p2['start_time'] or p2['end_time'] < p1['start_time'])
                    same_channel = (p1['channel_id'] == p2['channel_id'])
                    
                    # ÖNEMLİ: P2 de bu Gateway tarafından duyuluyor mu?
                    p2_dev = next((d for d in self.devices if d['id'] == p2['device_id']), None)
                    if not p2_dev: continue
                    p2_at_this_gw = p2_dev['all_gw_stats'].get(str(gw_id))
                    
                    if overlap and same_channel and p2_at_this_gw:
                        # LoRa PHY: P1 paketi bu girişimden kurtulabilir mi? (SIR Analizi)
                        p1_survives = check_collision_sir(p1['sf'], p2['sf'], stats['rssi'], p2_at_this_gw['rssi'])
                        
                        if not p1_survives:
                            collision = True
                            # Hata tipi tayini
                            if p1['sf'] == p2['sf']:
                                p1_collision_type = 'CO_SF'
                            else:
                                p1_collision_type = 'CROSS_SF'
                            break
                
                if not collision:
                    # Bu gateway paketi başarıyla aldı! (Belki capture effect sayesinde, belki de temiz kanal)
                    packet_received_by_any_gw = True
                    # Başarılı alım sonrası ACK penceresi için GW'yı meşgul et
                    ack_start = p1['end_time'] + 1.0
                    ack_end = ack_start + (calculate_time_on_air(10, p1['sf']) / 1000)
                    gw_busy_slots[gw_id].append((ack_start, ack_end))
                    break
            
            if packet_received_by_any_gw:
                p1['status'] = 'SUCCESS'
                success_count += 1
                device_stats[dev_id]['success'] += 1
            else:
                p1['status'] = 'FAILED'
                if is_blind: 
                    blindness_count += 1
                elif p1_collision_type == 'CO_SF':
                    co_sf_collisions += 1
                    collision_count += 1
                elif p1_collision_type == 'CROSS_SF':
                    cross_sf_collisions += 1
                    collision_count += 1
                else:
                    collision_count += 1 # Genel çakışma

        # Cihaz listesine PDR ekle
        for dev in self.devices:
            d_stat = device_stats[dev['id']]
            dev['pdr'] = (d_stat['success'] / d_stat['total'] * 100) if d_stat['total'] > 0 else 100

        pdr = (success_count / len(self.packets)) * 100 if self.packets else 0
        return {
            'total_packets': len(self.packets),
            'success': success_count,
            'collision': collision_count,
            'co_sf_collisions': co_sf_collisions,
            'cross_sf_collisions': cross_sf_collisions,
            'blindness': blindness_count,
            'pdr': pdr
        }
