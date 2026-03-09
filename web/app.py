import os
import sys

# Projenin kök dizinini sys.path'e ekle (Importlardan ÖNCE olmalı)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import json
import time
import os
import shutil
from datetime import datetime
from core.simulation import SmartCitySimulation
from core.traffic_sim import TrafficSimulator
from core import visualizer

app = Flask(__name__, static_folder='static')
CORS(app)

# Resim dizinini belirle
IMAGES_DIR = os.path.join(BASE_DIR, 'assets', 'plots')
HISTORY_DIR = os.path.join(BASE_DIR, 'assets', 'history')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/html/<path:path>')
def send_html(path):
    return send_from_directory(app.static_folder, path)

@app.route('/images/<path:path>')
def send_images(path):
    print(f"Serving image: {path} from {IMAGES_DIR}")
    return send_from_directory(IMAGES_DIR, path)

@app.route('/api/run-simulation', methods=['POST'])
def run_simulation():
    data = request.json
    num_bins = int(data.get('num_bins', 100))
    area_size = float(data.get('area_size', 5000))
    num_gateways = int(data.get('num_gateways', 4))
    is_full_suite = data.get('full_suite', False)
    scenario = data.get('scenario', 'NORMAL')

    def generate():
        logs = []
        def log_yield(msg):
            import sys
            print(f"[LOG] {msg}")
            sys.stdout.flush()
            return f"data: LOG:{msg}\n\n"

        try:
            yield log_yield(f"Simülasyon başlatılıyor (Senaryo: {scenario})...")
            
            # 1. Simülasyon (Hibrit Mod)
            if scenario == 'FAILURE':
                yield log_yield("KRİZ MODU: GW0 devre dışı! Diğer Gateway'ler yükü devralıyor...")
            elif scenario == 'STORM':
                yield log_yield("HAVA DURUMU: Şiddetli fırtına! Sinyal kaybı ve değişkenlik artırıldı.")
                
            yield log_yield(f"{num_bins} adet hibrit cihaz {area_size}m² alana yerleştiriliyor...")
            time.sleep(0.5) 
            sim = SmartCitySimulation(num_bins=num_bins, area_size=area_size, num_gateways=num_gateways, scenario=scenario)
            
            yield log_yield("Cihaz Profilleri Tanımlanıyor: Aydınlatma, Su Sayaçları, Hava Sensörleri...")
            results = sim.run_analysis()
            
            # 2. Trafik (Farklı Interval'lar)
            yield log_yield("Dinamik trafik senaryosu oluşturuluyor (Farklı cihaz sıklıkları)...")
            traffic = TrafficSimulator(results, duration_seconds=1800)
            traffic.generate_traffic(scenario=scenario)
            
            yield log_yield("Paket çakışmaları ve ağ kapasite analizi yapılıyor...")
            traffic_stats = traffic.run_collision_analysis()
            
            # 3. Grafikler (Adım Adım Loglama)
            yield log_yield("Görselleştirme Katmanı Hazırlanıyor...")
            
            try:
                yield log_yield("Adım 1/9: Hibrit Şehir Haritası üretiliyor...")
                visualizer.plot_spatial_distribution(sim)
                
                yield log_yield("Adım 2/9: Kapsama Isı Haritası (Grid Analizi) üretiliyor...")
                visualizer.plot_coverage_heatmap(sim, results)
                
                yield log_yield("Adım 3/9: Mahalle Bazlı PDR analizi yapılıyor...")
                visualizer.plot_neighborhood_stats(results)
                
                yield log_yield("Adım 4/9: Sinyal Kalitesi (RSSI/SNR) dağılımı üretiliyor...")
                visualizer.plot_signal_quality(results)
                
                yield log_yield("Adım 5/9: Pil Ömrü ve Enerji tüketim projeksiyonu üretiliyor...")
                visualizer.plot_energy_analysis(results)
                
                yield log_yield("Adım 6/9: Cihaz Tipi spesifik performans stats üretiliyor...")
                visualizer.plot_device_type_stats(results)
                
                yield log_yield("Adım 7/9: LoRaWAN Akademik Kısıtlar (MTU/Duty) grafiği üretiliyor...")
                visualizer.plot_academic_constraints(results)
                
                yield log_yield("Adım 8/9: Link Margin (Bağlantı Payı) ispatı üretiliyor...")
                visualizer.plot_link_margin(results)
                
                yield log_yield("Adım 9/10: Sub-Noise (Gürültü Altı İletişim) analizi üretiliyor...")
                visualizer.plot_signal_vs_noise(results)

                yield log_yield("Adım 10/10: Gateway Diversity (Yedeklilik) haritası üretiliyor...")
                visualizer.plot_gateway_redundancy(sim)
                
            except Exception as plot_err:
                yield log_yield(f"GÖRSELLEŞTİRME HATASI: {str(plot_err)}")
                print(f"Plot Error: {plot_err}")
            
            if is_full_suite:
                yield log_yield("İleri Analiz: Teorik limitler ve PDR stres testi (Ağ Kapasite) işleniyor...")
                visualizer.plot_theoretical_limits()
                visualizer.plot_collision_analysis(results)
                
                yield log_yield("KRİTİK: Bilimsel PDR Stres Testi (Bu işlem uzun sürebilir, bağlantıyı kesmeyin)...")
                visualizer.plot_pdr_analysis(SmartCitySimulation, area_size=area_size) 
            
            yield log_yield("Simülasyon ve tüm bilimsel analizler başarıyla tamamlandı.")
            yield log_yield("Sonuçlar arşivleniyor ve raporlanıyor...")
            
            stats_data = {
                'num_bins': num_bins,
                'num_gateways': len(sim.gateways),
                'pdr': round(traffic_stats['pdr'], 2),
                'blindness': traffic_stats['blindness'],
                'collision': traffic_stats['collision'],
                'avg_latency': round(sum(r['toa'] for r in results) / len(results), 2) if results else 0,
                'scenario': scenario
            }
            
            # --- ARŞİVLEME ---
            sim_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_path = os.path.join(HISTORY_DIR, f"sim_{sim_id}")
            os.makedirs(os.path.join(history_path, "plots"), exist_ok=True)
            
            with open(os.path.join(history_path, "results.json"), "w") as f:
                json.dump({'stats': stats_data, 'logs': logs}, f)
            
            for plot_file in os.listdir(IMAGES_DIR):
                if plot_file.endswith(".png"):
                    shutil.copy(os.path.join(IMAGES_DIR, plot_file), os.path.join(history_path, "plots", plot_file))

            final_data = {
                'status': 'success',
                'sim_id': sim_id,
                'stats': {
                    **stats_data,
                    'img_map_path': '/images/city_map_sf_distribution.png',
                    'img_heatmap_path': '/images/coverage_heatmap.png',
                    'img_neighborhood_path': '/images/neighborhood_analysis.png',
                    'img_pdr_path': '/images/network_pdr_analysis.png',
                    'img_energy_path': '/images/energy_analysis.png',
                    'img_signal_path': '/images/signal_quality.png',
                    'img_device_type_path': '/images/device_type_analysis.png',
                    'img_academic_path': '/images/academic_constraints.png',
                    'img_margin_path': '/images/link_margin_analysis.png',
                    'img_signal_noise_path': '/images/signal_noise_analysis.png'
                }
            }
            yield f"data: RESULT:{json.dumps(final_data)}\n\n"
            
        except Exception as e:
            import traceback
            error_msg = f"KRİTİK HATA: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            yield f"data: {error_msg}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/api/history', methods=['GET'])
def get_history():
    if not os.path.exists(HISTORY_DIR):
        return jsonify([])
    
    history_list = []
    for folder in sorted(os.listdir(HISTORY_DIR), reverse=True):
        if folder.startswith("sim_"):
            try:
                with open(os.path.join(HISTORY_DIR, folder, "results.json"), "r") as f:
                    data = json.load(f)
                    history_list.append({
                        'id': folder,
                        'date': datetime.strptime(folder.replace("sim_", ""), "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S"),
                        'pdr': data['stats']['pdr'],
                        'devices': data['stats']['num_bins']
                    })
            except:
                continue
    return jsonify(history_list)

@app.route('/api/history/<sim_id>', methods=['GET'])
def get_history_detail(sim_id):
    path = os.path.join(HISTORY_DIR, sim_id)
    if not os.path.exists(path):
        return jsonify({'status': 'error', 'message': 'Not found'}), 404
        
    with open(os.path.join(path, "results.json"), "r") as f:
        return jsonify(json.load(f))

# Geçmiş grafiklerini servis et
@app.route('/history-images/<sim_id>/<path:filename>')
def serve_history_image(sim_id, filename):
    return send_from_directory(os.path.join(HISTORY_DIR, sim_id, "plots"), filename)

if __name__ == '__main__':
    # Klasörler yoksa oluştur
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(HISTORY_DIR, exist_ok=True)
    # use_reloader=False: Grafik dosyaları kaydedildiğinde sunucunun kapanmasını engeller
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
