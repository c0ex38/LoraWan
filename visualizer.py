import matplotlib.pyplot as plt
import numpy as np
from utils import calculate_time_on_air, calculate_bit_rate

def plot_sf_analysis(results):
    sfs = [r['sf'] for r in results]
    toas = [r['toa'] for r in results]
    bit_rates = [r['bit_rate'] for r in results]
    distances = [r['distance'] for r in results]

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
    fig.tight_layout()
    plt.savefig('images/sf_analysis_plot.png')
    print("Graph saved as images/sf_analysis_plot.png")

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

    plt.tight_layout()
    plt.savefig('images/theoretical_limits.png')
    print("Theoretical limits graph saved as images/theoretical_limits.png")

def plot_spatial_distribution(sim):
    """
    Çöp kutularının konumlarını ve SF bölgelerini harita üzerinde gösterir.
    """
    plt.figure(figsize=(10, 10))
    
    # Gateway
    plt.scatter(0, 0, c='red', marker='H', s=200, label='Gateway', zorder=5)
    
    # SF Bölgeleri (Halkalar)
    circles = [1000, 2000, 3000, 4000, 5000]
    colors = ['#e1f5fe', '#b3e5fc', '#81d4fa', '#4fc3f7', '#29b6f6', '#039be5']
    labels = ['SF7', 'SF8', 'SF9', 'SF10', 'SF11', 'SF12']
    
    for i, r in enumerate(circles):
        circle = plt.Circle((0, 0), r, fill=False, linestyle='--', alpha=0.3)
        plt.gca().add_patch(circle)
    
    # Çöp Kutuları
    scatter = plt.scatter(sim.bin_positions[:, 0], sim.bin_positions[:, 1], 
                         c=sim.bin_sfs, cmap='viridis', s=100, edgecolors='black', label='Smart Bins')
    
    plt.colorbar(scatter, label='Spreading Factor (SF)')
    plt.title('Akıllı Çöp Kutuları Konum ve SF Dağılımı (Şehir Haritası)')
    plt.xlabel('Mesafe (X - metre)')
    plt.ylabel('Mesafe (Y - metre)')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    plt.axis('equal')
    plt.savefig('images/city_map_sf_distribution.png')
    print("City map saved as images/city_map_sf_distribution.png")

def plot_energy_analysis(results):
    """
    SF bazlı enerji tüketimi ve pil ömrü tahmini grafiği.
    """
    sfs = sorted(list(set([r['sf'] for r in results])))
    avg_energy = []
    avg_life = []
    
    for sf in sfs:
        energies = [r['energy'] for r in results if r['sf'] == sf]
        lives = [r['battery_life'] for r in results if r['sf'] == sf]
        avg_energy.append(np.mean(energies))
        avg_life.append(np.mean(lives))

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
    fig.tight_layout()
    plt.savefig('images/energy_analysis.png')
    print("Energy analysis plot saved as images/energy_analysis.png")

def plot_collision_analysis(results):
    """
    Ağ yoğunluğu arttıkça çakışma olasılığını analiz eder.
    """
    from utils import calculate_collision_probability
    
    device_counts = np.linspace(10, 1000, 10)
    intervals = [3600, 600, 60] # 1 saat, 10 dk, 1 dk
    labels = ['1 Hour', '10 Mins', '1 Min']
    
    plt.figure(figsize=(10, 6))
    
    # SF10 için ortalama ToA kullanalım
    avg_toa = np.mean([r['toa'] for r in results if r['sf'] == 10])
    
    for interval, label in zip(intervals, labels):
        probs = [calculate_collision_probability(n, avg_toa, interval) * 100 for n in device_counts]
        plt.plot(device_counts, probs, marker='o', label=f'Interval: {label}')
        
    plt.title(f'Packet Collision Probability (SF10, ToA: {avg_toa:.1f}ms)')
    plt.xlabel('Number of Devices per Gateway')
    plt.ylabel('Collision Probability (%)')
    plt.grid(True)
    plt.legend()
    plt.savefig('images/collision_analysis.png')
    print("Collision analysis plot saved as images/collision_analysis.png")

def plot_signal_quality(results):
    """
    Mesafe ve SF'ye göre RSSI/SNR dağılımı.
    """
    distances = [r['distance'] for r in results]
    rssis = [r['rssi'] for r in results]
    snrs = [r['snr'] for r in results]
    sfs = [r['sf'] for r in results]

    plt.figure(figsize=(12, 5))

    # RSSI vs Distance
    plt.subplot(1, 2, 1)
    scatter = plt.scatter(distances, rssis, c=sfs, cmap='viridis', edgecolors='k')
    plt.title('RSSI vs Distance (Shadowing Effect)')
    plt.xlabel('Distance (m)')
    plt.ylabel('RSSI (dBm)')
    plt.colorbar(scatter, label='SF')
    plt.grid(True)

    # SNR vs SF
    plt.subplot(1, 2, 2)
    plt.boxplot([ [r['snr'] for r in results if r['sf'] == sf] for sf in range(7, 13) ], 
                tick_labels=range(7, 13))
    plt.title('SNR Distribution per SF')
    plt.xlabel('Spreading Factor (SF)')
    plt.ylabel('SNR (dB)')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('images/signal_quality.png')
    print("Signal quality plot saved as images/signal_quality.png")

def plot_pdr_analysis(sim_class, area_size=5000):
    """
    Farklı cihaz yoğunluklarında Packet Delivery Ratio (PDR) analizi.
    """
    from traffic_sim import TrafficSimulator
    
    device_counts = [20, 50, 100, 200, 500]
    pdrs = []
    
    print("\nRunning Stress Test for PDR Analysis...")
    for count in device_counts:
        temp_sim = sim_class(num_bins=count, area_size=area_size)
        results = temp_sim.run_analysis()
        traffic = TrafficSimulator(results, duration_seconds=1800) # 30 dk simülasyon
        traffic.generate_traffic(interval_seconds=300) # 5 dk aralık
        stats = traffic.run_collision_analysis()
        pdrs.append(stats['pdr'])
        print(f"Devices: {count} | PDR: {stats['pdr']:.2f}%")

    plt.figure(figsize=(10, 6))
    plt.plot(device_counts, pdrs, marker='s', color='purple', linewidth=2)
    plt.axhline(y=90, color='r', linestyle='--', label='90% Reliability Threshold')
    plt.title('Network Scalability: Packet Delivery Ratio (PDR)')
    plt.xlabel('Number of Smart Bins')
    plt.ylabel('PDR (%)')
    plt.grid(True)
    plt.legend()
    plt.savefig('images/network_pdr_analysis.png')
    print("PDR analysis plot saved as images/network_pdr_analysis.png")

if __name__ == "__main__":
    from simulation import SmartCitySimulation
    sim = SmartCitySimulation(num_bins=50, area_size=7000)
    results = sim.run_analysis()
    plot_sf_analysis(results)
    plot_theoretical_limits()
    plot_spatial_distribution(sim)
    plot_energy_analysis(results)
    plot_collision_analysis(results)
