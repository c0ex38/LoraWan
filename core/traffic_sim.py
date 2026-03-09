import numpy as np
from .utils import calculate_time_on_air, check_collision_sir

class TrafficSimulator:
    def __init__(self, simulation_results, duration_seconds=3600, num_channels=8):
        self.devices = simulation_results
        self.duration = duration_seconds
        self.num_channels = num_channels
        self.packets = []
        
    def generate_traffic(self, interval_seconds=600):
        self.packets = []
        for dev in self.devices:
            current_time = np.random.uniform(0, interval_seconds)
            toa_s = dev['toa'] / 1000
            
            while current_time < self.duration:
                self.packets.append({
                    'device_id': dev['id'],
                    'start_time': current_time,
                    'end_time': current_time + toa_s,
                    'sf': dev['sf'],
                    'rssi': dev['rssi'],
                    'channel_id': np.random.randint(0, self.num_channels), # Rastgele kanal
                    'gateway_id': dev['gateway_id'],
                    'status': 'SUCCESS'
                })
                current_time += interval_seconds + np.random.uniform(-10, 10)
        
        self.packets.sort(key=lambda x: x['start_time'])
        return self.packets

    def run_collision_analysis(self):
        """
        Zaman ekseninde çakışmaları ve Gateway körlüğünü (Half-Duplex) kontrol eder.
        """
        success_count = 0
        collision_count = 0
        blindness_count = 0
        
        # Gateway meşguliyet takibi: {gw_id: [(start, end), ...]}
        gw_busy_slots = {i: [] for i in range(10)} # Max 10 GW varsayalım
        
        # Önce tüm başarılı uplink'ler için downlink pencereleri oluşturulmalı
        # Ancak bu basitleştirme adına paket sırasıyla gidelim
        
        for i, p1 in enumerate(self.packets):
            gw_id = p1['gateway_id']
            
            # 1. Gateway Körlüğü Kontrolü (Half-Duplex)
            # Eğer p1 ulaştığında Gateway başka bir ACK gönderiyorsa paket kaybolur.
            is_blind = False
            for busy_start, busy_end in gw_busy_slots[gw_id]:
                if not (p1['end_time'] < busy_start or p1['start_time'] > busy_end):
                    is_blind = True
                    break
            
            if is_blind:
                p1['status'] = 'GW_BLIND'
                blindness_count += 1
                continue

            # 2. Uplink-Uplink Çakışma Kontrolü (SIR/Orthogonality)
            for j, p2 in enumerate(self.packets):
                if i == j: continue
                overlap = not (p1['end_time'] < p2['start_time'] or p2['end_time'] < p1['start_time'])
                same_channel = (p1['channel_id'] == p2['channel_id'])
                if overlap and same_channel:
                    p1_survives = check_collision_sir(p1['sf'], p2['sf'], p1['rssi'], p2['rssi'])
                    if not p1_survives:
                        p1['status'] = 'COLLIDED'
                        collision_count += 1
                        break
            
            # 3. ACK Gönderimi ve Gateway'i Meşgul Etme
            if p1['status'] == 'SUCCESS':
                success_count += 1
                # LoRaWAN RX1 Penceresi: Uplink bittikten 1s sonra başlar
                # ACK süresi (Downlink ToA) yaklaşık bir Uplink kadardır
                ack_start = p1['end_time'] + 1.0
                ack_end = ack_start + (calculate_time_on_air(10, p1['sf']) / 1000)
                gw_busy_slots[gw_id].append((ack_start, ack_end))
        
        pdr = (success_count / len(self.packets)) * 100 if self.packets else 0
        return {
            'total_packets': len(self.packets),
            'success': success_count,
            'collision': collision_count,
            'blindness': blindness_count, # Gateway meşgulken gelenler
            'pdr': pdr
        }
