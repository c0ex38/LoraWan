from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import json
from core.simulation import SmartCitySimulation
from core.traffic_sim import TrafficSimulator
from core import visualizer

app = Flask(__name__, static_folder='static')
CORS(app)

# Ana dizini ve resim dizinini belirle
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, 'assets', 'plots')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/html/<path:path>')
def send_html(path):
    return send_from_directory(app.static_folder, path)

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory(IMAGES_DIR, path)

@app.route('/api/run-simulation', methods=['POST'])
def run_simulation():
    try:
        data = request.json
        num_bins = int(data.get('num_bins', 100))
        area_size = int(data.get('area_size', 5000))
        num_gateways = int(data.get('num_gateways', 4))
        
        print(f"Running simulation: {num_bins} bins, {area_size}m, {num_gateways} GWs")
        
        # 1. Simülasyonu çalıştır
        sim = SmartCitySimulation(num_bins=num_bins, area_size=area_size, num_gateways=num_gateways)
        results = sim.run_analysis()
        
        # 2. Trafik Analizi
        traffic = TrafficSimulator(results, duration_seconds=1800)
        traffic.generate_traffic(interval_seconds=300)
        stats = traffic.run_collision_analysis()
        
        # 3. Grafikleri Güncelle
        visualizer.plot_spatial_distribution(sim)
        visualizer.plot_signal_quality(results)
        visualizer.plot_energy_analysis(results)
        visualizer.plot_pdr_analysis(SmartCitySimulation, area_size=area_size) # PDR analizi tüm sınıfı kullanır
        
        # 4. Yanıtı hazırla
        response = {
            'status': 'success',
            'stats': {
                'num_bins': num_bins,
                'num_gateways': num_gateways,
                'pdr': round(stats['pdr'], 2),
                'blindness': stats['blindness'],
                'collision': stats['collision'],
                'img_map_path': '/images/city_map_sf_distribution.png',
                'img_pdr_path': '/images/network_pdr_analysis.png',
                'img_energy_path': '/images/energy_analysis.png',
                'img_signal_path': '/images/signal_quality.png'
            }
        }
        return jsonify(response)
        
    except Exception as e:
        print(f"Simulation Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Resim klasörü yoksa oluştur
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    app.run(host='0.0.0.0', port=8000, debug=True)
