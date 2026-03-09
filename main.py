import os
from core.simulation import SmartCitySimulation
from core.visualizer import (plot_sf_analysis, plot_theoretical_limits, plot_spatial_distribution, 
                        plot_energy_analysis, plot_collision_analysis, plot_signal_quality, plot_pdr_analysis)

def main():
    print("--- LoRaWAN SF Analysis Simulation Starting ---")
    
    # 1. Klasör düzenini kontrol et
    if not os.path.exists("images"):
        os.makedirs("images")
        print("Created 'images' directory.")

    # 2. Simülasyonu yapılandır ve çalıştır (FAZ 4: Profesyonel Seviye)
    num_bins = 1000   # 1000 Akıllı Çöp Kutusu
    area_size = 10000 # 10km x 10km Şehir Alanı
    num_gateways = 4  # 4 Gateway (Kule)
    
    print(f"Configuring Pro Simulation: {num_bins} bins, {area_size}m area, {num_gateways} Gateways...")
    sim = SmartCitySimulation(num_bins=num_bins, area_size=area_size, num_gateways=num_gateways)
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
