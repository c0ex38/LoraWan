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
            logs.append(msg)
            return f"data: {msg}\n\n"

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
            
            # 3. Grafikler
            yield log_yield("Hibrit şehir haritası ve kapsama analizleri üretiliyor...")
            visualizer.plot_spatial_distribution(sim)
            visualizer.plot_coverage_heatmap(sim, results)
            visualizer.plot_neighborhood_stats(results)
            visualizer.plot_signal_quality(results)
            visualizer.plot_energy_analysis(results)
            visualizer.plot_device_type_stats(results) # NEW
            
            if is_full_suite:
                yield log_yield("İleri Analiz: Teorik limitler ve detaylı PDR stres testi işleniyor...")
                visualizer.plot_theoretical_limits()
                visualizer.plot_collision_analysis(results)
                visualizer.plot_pdr_analysis(SmartCitySimulation, area_size=area_size) 
            
            yield log_yield("Simülasyon ve hibrit analizler başarıyla tamamlandı.")
            
            stats_data = {
                'num_bins': num_bins,
                'num_gateways': len(sim.gateways),
                'pdr': round(traffic_stats['pdr'], 2),
                'blindness': traffic_stats['blindness'],
                'collision': traffic_stats['collision'],
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
                    'img_device_type_path': '/images/device_type_analysis.png'
                }
            }
            yield f"data: RESULT:{json.dumps(final_data)}\n\n"
            
        except Exception as e:
            yield f"data: HATA: {str(e)}\n\n"

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
    app.run(host='0.0.0.0', port=8000, debug=True)
