def _save_and_clean(filename, title=None):
    """Grafik kaydetme ve temizleme işlemlerini yapan yardımcı fonksiyon."""
    plt.tight_layout()
    path = f'assets/plots/{filename}'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close('all')
    if title:
        print(f"[Görselleştirme] {title} -> {path}")

def plot_sf_analysis(results):
    toas = [r['toa'] for r in results]
    bit_rates = [r['bit_rate'] for r in results]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    color = 'tab:blue'
    ax1.set_xlabel('Bin ID / Distance (m)')
    ax1.set_ylabel('Time on Air (ms)', color=color)
    ax1.scatter(range(len(results)), toas, color=color, label='ToA (ms)')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Bit Rate (bps)', color=color)
    ax2.plot(range(len(results)), bit_rates, color=color, marker='x', linestyle='--', label='Bit Rate')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('LoRaWAN SF Analysis: Time on Air vs Data Rate')
    _save_and_clean('sf_analysis_plot.png', "SF Analizi")

def plot_theoretical_limits():
    sfs = range(7, 13)
    toas = [calculate_time_on_air(10, sf) for sf in sfs]
    bit_rates = [calculate_bit_rate(sf) for sf in sfs]

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.bar(sfs, toas, color='skyblue')
    plt.title('Theoretical Time on Air (10 bytes)')
    plt.xlabel('Spreading Factor (SF)')
    plt.ylabel('ToA (ms)')

    plt.subplot(1, 2, 2)
    plt.plot(sfs, bit_rates, marker='o', color='orange')
    plt.title('Theoretical Bit Rate')
    plt.xlabel('Spreading Factor (SF)')
    plt.ylabel('bps')

    _save_and_clean('theoretical_limits.png', "Teorik Limitler")

def plot_spatial_distribution(sim):
    plt.figure(figsize=(12, 12))
    markers = {'BIN': 'o', 'LIGHT': '^', 'WATER': 's', 'AIR': 'D'}
    for d_type in markers:
        idx = [i for i, t in enumerate(sim.device_types) if t == d_type]
        if idx:
            plt.scatter(sim.bin_positions[idx, 0], sim.bin_positions[idx, 1], 
                        marker=markers[d_type], label=f'Cihaz: {d_type}', 
                        c=[sim.bin_sfs[i] for i in idx], cmap='viridis', 
                        s=100, edgecolors='white', vmin=7, vmax=12)
    
    plt.colorbar(label='Spreading Factor (SF)')
    plt.title(f'Hibrit Şehir Ağ Haritası: {len(sim.gateways)} Gateway & {sim.num_bins} Karışık Cihaz')
    plt.xlabel('Mesafe (X - metre)')
    plt.ylabel('Mesafe (Y - metre)')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    plt.axis('equal')
    _save_and_clean('city_map_sf_distribution.png', "Şehir Haritası")

def plot_device_type_stats(results):
    types = sorted(list(set([r['type'] for r in results])))
    pdr_means = []
    life_means = []
    
    for t in types:
        type_res = [r for r in results if r['type'] == t]
        pdr_means.append(np.mean([r['pdr'] for r in type_res]) if type_res else 0)
        life_means.append(np.mean([r['battery_life'] for r in type_res]) if type_res else 0)
        
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(types, pdr_means, color='#3b82f6', alpha=0.6, label='Ortalama PDR (%)')
    ax1.set_ylabel('Başarı Oranı (PDR %)', color='#1d4ed8')
    ax1.set_ylim(0, 105)
    
    ax2 = ax1.twinx()
    ax2.plot(types, life_means, color='#ef4444', marker='o', linewidth=3, label='Ortalama Pil (Yıl)')
    ax2.set_ylabel('Tahmini Pil Ömrü (Yıl)', color='#b91c1c')
    
    plt.title('Hibrit Hizmet Analizi: Cihaz Tipi Bazlı Performans & Ömür')
    _save_and_clean('device_type_analysis.png', "Cihaz Tipi İstatistikleri")

def plot_energy_analysis(results):
    sfs = sorted(list(set([r['sf'] for r in results])))
    avg_energy = []
    avg_life = []
    
    for sf in sfs:
        energies = [r['energy'] for r in results if r['sf'] == sf]
        lives = [r['battery_life'] for r in results if r['sf'] == sf]
        avg_energy.append(np.mean(energies) if energies else 0)
        avg_life.append(np.mean(lives) if lives else 0)

    fig, ax1 = plt.subplots(figsize=(10, 6))
    color = 'tab:red'
    ax1.set_xlabel('Spreading Factor (SF)')
    ax1.set_ylabel('Energy per Packet (mJ)', color=color)
    ax1.bar(sfs, avg_energy, color=color, alpha=0.6, label='Energy Consumption')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:green'
    ax2.set_ylabel('Estimated Battery Life (Years)', color=color)
    ax2.plot(sfs, avg_life, color=color, marker='D', linewidth=2, label='Battery Life')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('LoRaWAN SF Impact on Battery Life and Energy')
    _save_and_clean('energy_analysis.png', "Enerji Analizi")

def plot_collision_analysis(results):
    from .utils import calculate_collision_probability
    device_counts = np.linspace(10, 1000, 10)
    intervals = [3600, 600, 60]
    labels = ['1 Hour', '10 Mins', '1 Min']
    
    plt.figure(figsize=(10, 6))
    avg_toa = np.mean([r['toa'] for r in results]) if results else 100
    
    for interval, label in zip(intervals, labels):
        probs = [calculate_collision_probability(n, avg_toa, interval) * 100 for n in device_counts]
        plt.plot(device_counts, probs, marker='o', label=f'Interval: {label}')
        
    plt.title(f'Packet Collision Probability (SF10, ToA: {avg_toa:.1f}ms)')
    plt.xlabel('Number of Devices per Gateway')
    plt.ylabel('Collision Probability (%)')
    plt.grid(True)
    plt.legend()
    _save_and_clean('collision_analysis.png', "Basit Çakışma Analizi")

def plot_signal_quality(results):
    distances = [r['distance'] for r in results]
    rssis = [r['rssi'] for r in results]
    sfs = [r['sf'] for r in results]

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    scatter = plt.scatter(distances, rssis, c=sfs, cmap='viridis', edgecolors='k')
    plt.title('RSSI vs Distance (Shadowing Effect)')
    plt.xlabel('Distance (m)')
    plt.ylabel('RSSI (dBm)')
    plt.colorbar(scatter, label='SF')
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.boxplot([ [r['snr'] for r in results if r['sf'] == sf] for sf in range(7, 13) ], 
                tick_labels=range(7, 13))
    plt.title('SNR Distribution per SF')
    plt.xlabel('Spreading Factor (SF)')
    plt.ylabel('SNR (dB)')
    plt.grid(True)

    _save_and_clean('signal_quality.png', "Sinyal Kalitesi")

def plot_pdr_analysis(sim_class, area_size=5000):
    from .traffic_sim import TrafficSimulator
    device_counts = [50, 200, 500, 1000, 2000]
    pdrs, collisions, blindness = [], [], []
    
    for count in device_counts:
        temp_sim = sim_class(num_bins=count, area_size=area_size, num_gateways=4)
        results = temp_sim.run_analysis()
        traffic = TrafficSimulator(results, duration_seconds=1800)
        traffic.generate_traffic(interval_seconds=300)
        stats = traffic.run_collision_analysis()
        
        pdrs.append(stats['pdr'])
        total = stats['total_packets']
        collisions.append((stats['collision'] / total) * 100 if total > 0 else 0)
        blindness.append((stats['blindness'] / total) * 100 if total > 0 else 0)
        del temp_sim

    plt.figure(figsize=(12, 7))
    plt.subplot(2, 1, 1)
    plt.plot(device_counts, pdrs, marker='s', color='purple', linewidth=2, label='Success Rate (PDR)')
    plt.axhline(y=90, color='r', linestyle='--', label='90% Reliability')
    plt.title('End-to-End Reliability with Downlink ACK')
    plt.ylabel('PDR (%)')
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.bar(range(len(device_counts)), collisions, label='Loss: Collision', color='orange')
    plt.bar(range(len(device_counts)), blindness, bottom=collisions, label='Loss: GW Blindness (Half-Duplex)', color='red')
    plt.xticks(range(len(device_counts)), device_counts)
    plt.title('Analysis of Packet Loss Causes')
    plt.xlabel('Number of Smart Bins')
    plt.ylabel('Loss Rate (%)')
    plt.legend()
    plt.grid(axis='y', linestyle=':')

    _save_and_clean('network_pdr_analysis.png', "Genel PDR Analizi")

def plot_coverage_heatmap(sim, results):
    from scipy.interpolate import griddata
    x = sim.bin_positions[:, 0]
    y = sim.bin_positions[:, 1]
    z = [r['rssi'] for r in results]
    
    half_size = sim.area_size / 2
    xi = np.linspace(-half_size, half_size, 100)
    yi = np.linspace(-half_size, half_size, 100)
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata((x, y), z, (xi, yi), method='linear')
    
    plt.figure(figsize=(10, 8))
    cp = plt.contourf(xi, yi, zi, cmap='RdYlGn', alpha=0.7, levels=20)
    plt.colorbar(cp, label='Sinyal Gücü (RSSI - dBm)')
    
    for i, gw in enumerate(sim.gateways):
        plt.scatter(gw[0], gw[1], c='black', marker='H', s=200, label=f'GW{i}' if i==0 else "")
        
    plt.title('Kapsama Isı Haritası: Zayıf Sinyal (Ölü Bölge) Analizi')
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    _save_and_clean('coverage_heatmap.png', "Kapsama Isı Haritası")

def plot_neighborhood_stats(results):
    near = [r['pdr'] for r in results if r['distance'] < 1500]
    mid = [r['pdr'] for r in results if 1500 <= r['distance'] < 3000]
    far = [r['pdr'] for r in results if r['distance'] >= 3000]
    
    labels = ['Merkez', 'Çevre', 'Kırsal']
    means = [np.mean(near) if near else 0, np.mean(mid) if mid else 0, np.mean(far) if far else 0]
    
    plt.figure(figsize=(8, 6))
    plt.bar(labels, means, color=['#3b82f6', '#10b981', '#f59e0b'])
    plt.title('Bölgesel Verimlilik Kıyaslaması (Mahalle Bazlı PDR)')
    plt.ylabel('Başarı Oranı (%)')
    plt.ylim(0, 105)
    for i, v in enumerate(means):
        plt.text(i, v + 2, f"%{v:.1f}", ha='center', fontweight='bold')
        
    _save_and_clean('neighborhood_analysis.png', "Mahalle Analizi")

def plot_academic_constraints(results):
    sfs = sorted(list(set([r['sf'] for r in results])))
    avg_off_time, mtus = [], []
    
    for sf in sfs:
        sf_res = [r for r in results if r['sf'] == sf]
        avg_off_time.append(np.mean([r['off_time'] for r in sf_res]) if sf_res else 0)
        mtus.append(sf_res[0]['mtu_limit'] if sf_res else 0)
        
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(sfs, mtus, color='tab:blue', alpha=0.4, label='MTU Limit')
    ax1.set_ylabel('Max Payload / MTU (Bytes)', color='tab:blue')
    
    ax2 = ax1.twinx()
    ax2.plot(sfs, avg_off_time, color='tab:red', marker='s', linewidth=3, label='Duty Cycle Silence')
    ax2.set_ylabel('Required Off-Time (Seconds)', color='tab:red')
    
    plt.title('LoRaWAN Academic Constraints: MTU vs Duty Cycle Privacy')
    _save_and_clean('academic_constraints.png', "Akademik Kısıtlar")

def plot_link_margin(results):
    ids = range(len(results))
    snrs = [r['snr'] for r in results]
    req_snrs = [get_required_snr(r['sf']) for r in results]
    
    plt.figure(figsize=(12, 6))
    plt.plot(ids, snrs, label='Mevcut SNR (dB)', color='#3b82f6', marker='o', markersize=4, alpha=0.8)
    plt.plot(ids, req_snrs, label='Gereken Min. SNR', color='#ef4444', linestyle='--', linewidth=2)
    
    plt.fill_between(ids, req_snrs, snrs, where=(np.array(snrs) >= np.array(req_snrs)), color='green', alpha=0.2, label='Güvenli Bölge')
    plt.fill_between(ids, req_snrs, snrs, where=(np.array(snrs) < np.array(req_snrs)), color='red', alpha=0.3, label='Riskli')
    
    plt.title('Link Margin Analizi: Bağlantı Güvenlik Payı & ADR Potansiyeli')
    plt.xlabel('Cihaz ID')
    plt.ylabel('Sinyal Kalitesi (SNR - dB)')
    plt.legend()
    _save_and_clean('link_margin_analysis.png', "Link Margin Analizi")

def plot_signal_vs_noise(results):
    res_sample = results[:50]
    ids = range(len(res_sample))
    rssis = [r['rssi'] for r in res_sample]
    noise_floor = res_sample[0]['noise_floor'] if res_sample else -113
    
    plt.figure(figsize=(12, 6))
    plt.axhline(y=noise_floor, color='#ef4444', linestyle='--', linewidth=2, label=f'Noise Floor ({noise_floor:.1f} dBm)')
    plt.scatter(ids, rssis, c='#3b82f6', label='RSSI', alpha=0.7, edgecolors='white')
    plt.fill_between(ids, noise_floor, -145, color='gray', alpha=0.1, label='Sub-Noise Region')
    
    plt.title('LoRa Physics: Signal vs Noise (Sub-Noise Recovery Probability)')
    plt.xlabel('Cihaz Örneği (Sample)')
    _save_and_clean('signal_noise_analysis.png', "Signal vs Noise")

def plot_gateway_redundancy(sim):
    grid_res = 30
    half_size = sim.area_size / 2
    x = np.linspace(-half_size, half_size, grid_res)
    y = np.linspace(-half_size, half_size, grid_res)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)

    for i in range(grid_res):
        for j in range(grid_res):
            pos = np.array([X[i,j], Y[i,j]])
            count = 0
            for gw_pos in sim.gateways:
                d = np.linalg.norm(pos - gw_pos)
                if (sim.tx_power - calculate_path_loss(d)) > -120: 
                    count += 1
            Z[i,j] = count

    plt.figure(figsize=(10, 8))
    im = plt.pcolormesh(X, Y, Z, shading='auto', cmap='plasma', alpha=0.8)
    plt.colorbar(im, label='Kapsayan Gateway Sayısı (Redundancy)')
    plt.scatter(sim.gateways[:,0], sim.gateways[:,1], marker='^', s=200, color='white', edgecolors='black', label='Gateway')
    plt.title("Ağ Yedeklilik (Gateway Redundancy) Haritası")
    _save_and_clean('gateway_redundancy.png', "Yedeklilik Analizi")

def plot_spectral_efficiency(traffic_results):
    labels = ['Başarılı', 'Aynı SF Çakışma', 'Cross-SF Çakışma', 'Gateway Körlüğü']
    sizes = [traffic_results.get('success', 0), traffic_results.get('co_sf_collisions', 0), 
             traffic_results.get('cross_sf_collisions', 0), traffic_results.get('blindness', 0)]
    colors = ['#2ecc71', '#e67e22', '#e74c3c', '#95a5a6']
    
    f_labels, f_sizes, f_colors = [], [], []
    for l, s, c in zip(labels, sizes, colors):
        if s > 0:
            f_labels.append(l); f_sizes.append(s); f_colors.append(c)

    plt.figure(figsize=(10, 7))
    plt.pie(f_sizes, labels=f_labels, autopct='%1.1f%%', startangle=140, colors=f_colors, explode=[0.05]*len(f_sizes))
    plt.title("Ağ Spektral Verimlilik ve Girişim Dağılımı")
    _save_and_clean('spectral_efficiency.png', "Spektral Verimlilik")
    
def plot_reliability_heatmap(sim):
    plt.figure(figsize=(10, 8))
    failed = [i for i, s in enumerate(sim.device_statuses) if s == 'FAILED']
    active = [i for i, s in enumerate(sim.device_statuses) if s == 'ACTIVE']
    
    plt.scatter(sim.bin_positions[active, 0], sim.bin_positions[active, 1], c='blue', alpha=0.1)
    if failed:
        plt.scatter(sim.bin_positions[failed, 0], sim.bin_positions[failed, 1], marker='x', color='red', s=80, label='Hata')
    if sim.is_chaos and sim.jammer_pos is not None:
        plt.scatter(sim.jammer_pos[0], sim.jammer_pos[1], marker='*', color='yellow', s=300, edgecolors='black', label='Jammer')
        plt.gca().add_patch(plt.Circle(sim.jammer_pos, 500, color='red', fill=True, alpha=0.2))

    plt.title("Ağ Güvenilirlik ve Kaos Analizi Haritası")
    plt.legend()
    _save_and_clean('reliability_heatmap.png', "Güvenilirlik Haritası")

if __name__ == "__main__":
    from simulation import SmartCitySimulation
    sim = SmartCitySimulation(num_bins=50, area_size=7000)
    results = sim.run_analysis()
    plot_sf_analysis(results)
    plot_theoretical_limits()
    plot_spatial_distribution(sim)
    plot_energy_analysis(results)
    plot_collision_analysis(results)
