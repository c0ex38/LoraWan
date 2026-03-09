import numpy as np
from utils import calculate_time_on_air, check_collision_sir

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
        success_count = 0
        collision_count = 0
        
        for i, p1 in enumerate(self.packets):
            for j, p2 in enumerate(self.packets):
                if i == j: continue
                
                # ZAMAN ve KANAL çakışması var mı?
                overlap = not (p1['end_time'] < p2['start_time'] or p2['end_time'] < p1['start_time'])
                same_channel = (p1['channel_id'] == p2['channel_id'])
                
                if overlap and same_channel:
                    # LoRa SIR kontrolü
                    p1_survives = check_collision_sir(p1['sf'], p2['sf'], p1['rssi'], p2['rssi'])
                    if not p1_survives:
                        p1['status'] = 'COLLIDED'
                        collision_count += 1
                        break
            
            if p1['status'] == 'SUCCESS':
                success_count += 1
        
        pdr = (success_count / len(self.packets)) * 100 if self.packets else 0
        return {
            'total_packets': len(self.packets),
            'success': success_count,
            'collision': collision_count,
            'pdr': pdr
        }
