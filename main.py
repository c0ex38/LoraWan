import os
from simulation import SmartCitySimulation
from visualizer import (plot_sf_analysis, plot_theoretical_limits, plot_spatial_distribution, 
                        plot_energy_analysis, plot_collision_analysis, plot_signal_quality, plot_pdr_analysis)

def main():
    print("--- LoRaWAN SF Analysis Simulation Starting ---")
    
    # 1. Klasör düzenini kontrol et
    if not os.path.exists("images"):
        os.makedirs("images")
        print("Created 'images' directory.")

    # 2. Simülasyonu yapılandır ve çalıştır
    # num_bins: Çöp kutusu sayısı, area_size: Şehir yarıçapı (metre)
    num_bins = 50
    area_size = 8000
    
    print(f"Configuring simulation with {num_bins} smart bins in a {area_size}m area...")
    sim = SmartCitySimulation(num_bins=num_bins, area_size=area_size)
    results = sim.run_analysis()

    # 3. Görselleştirmeleri üret
    print("\nGenerating analysis plots...")
    plot_sf_analysis(results)
    plot_theoretical_limits()
    plot_spatial_distribution(sim)
    plot_energy_analysis(results)
    plot_signal_quality(results)
    plot_collision_analysis(results)
    
    # 4. Faz 3: Gerçek Zamanlı Trafik ve PDR Analizi
    plot_pdr_analysis(SmartCitySimulation, area_size=area_size)

    print("\n--- Simulation Completed Successfully! ---")
    print("All results and plots can be found in the 'images/' directory.")

if __name__ == "__main__":
    main()
