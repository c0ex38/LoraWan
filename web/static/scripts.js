document.addEventListener('DOMContentLoaded', () => {
    // Navigasyon tıklama efektleri
    const navItems = document.querySelectorAll('nav li');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });

    // Slider Değerlerini Güncelleme
    const sliders = [
        { id: 'num_bins', valId: 'bins_val' },
        { id: 'num_gateways', valId: 'gateways_val' },
        { id: 'area_size', valId: 'area_val', transform: (v) => (v/1000).toFixed(1) }
    ];

    sliders.forEach(s => {
        const slider = document.getElementById(s.id);
        const valSpan = document.getElementById(s.valId);
        slider.addEventListener('input', () => {
            valSpan.innerText = s.transform ? s.transform(slider.value) : slider.value;
        });
    });

    // Simülasyonu Çalıştırma
    const runBtn = document.getElementById('run_sim_btn');
    const runFullBtn = document.getElementById('run_full_sim_btn'); // Assuming this button exists for full suite

    async function runSimulation(url, button, originalText, isFull = false) {
        const num_bins = document.getElementById('num_bins').value;
        const num_gateways = document.getElementById('num_gateways').value;
        const area_size = document.getElementById('area_size').value;
        const logWindow = document.getElementById('sim_logs');

        button.disabled = true;
        button.innerText = 'SİMÜLASYON ÇALIŞIYOR...';
        button.style.opacity = '0.7';
        logWindow.innerHTML = ''; // Konsolu temizle

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    num_bins: num_bins,
                    num_gateways: num_gateways,
                    area_size: area_size,
                    full_suite: isFull,
                    scenario: document.getElementById('scenario_select').value
                })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let partialData = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                partialData += chunk;
                
                const lines = partialData.split('\n');
                partialData = lines.pop(); // Son (yarım kalmış olabilir) satırı sakla
                
                for (let lineText of lines) {
                    if (lineText.startsWith('data: ')) {
                        const content = lineText.replace('data: ', '').trim();
                        
                        if (content.startsWith('RESULT:')) {
                            // Final Sonuçlarını İşle
                            const data = JSON.parse(content.replace('RESULT:', ''));
                            updateUIWithResults(data);
                        } else if (content.startsWith('HATA:')) {
                            alert('Hata: ' + content);
                        } else if (content) {
                            // Normal Log
                            const div = document.createElement('div');
                            div.innerText = `> ${content}`;
                            logWindow.appendChild(div);
                            logWindow.scrollTop = logWindow.scrollHeight;
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Fetch error:', error);
            alert('Simülasyon sırasında bağlantı hatası oluştu.');
        } finally {
            button.disabled = false;
            button.innerText = originalText;
            button.style.opacity = '1';
        }
    }

    function updateUIWithResults(data) {
        if (data.status === 'success') {
            document.getElementById('stat_bins').innerText = data.stats.num_bins.toLocaleString();
            
            // Belediye Tasarruf Tahmini (Simülatif mantık: Cihaz başına PDR verimliliği ile)
            const baseSavingPerBin = 650; // TL (Güncel akaryakıt ve personel maliyet projeksiyonu)
            const totalSaving = Math.round(data.stats.num_bins * (data.stats.pdr / 100) * baseSavingPerBin);
            document.getElementById('stat_savings').innerText = `₺${(totalSaving/1000).toFixed(1)}K`;
            
            document.getElementById('stat_pdr').innerText = data.stats.pdr + '%';
            document.getElementById('stat_blindness').innerText = data.stats.blindness;

            const t = new Date().getTime();
            document.getElementById('img_map').src = `/images/city_map_sf_distribution.png?t=${t}`;
            document.getElementById('img_heatmap').src = `/images/coverage_heatmap.png?t=${t}`;
            document.getElementById('img_neighborhood').src = `/images/neighborhood_analysis.png?t=${t}`;
            document.getElementById('img_pdr').src = `/images/network_pdr_analysis.png?t=${t}`;
            document.getElementById('img_energy').src = `/images/energy_analysis.png?t=${t}`;
            document.getElementById('img_signal').src = `/images/signal_quality.png?t=${t}`;
            if (document.getElementById('img_device_type')) {
                document.getElementById('img_device_type').src = `/images/device_type_analysis.png?t=${t}`;
            }
            if (document.getElementById('img_academic')) {
                document.getElementById('img_academic').src = `/images/academic_constraints.png?t=${t}`;
            }
            
            if (document.getElementById('img_theoretical')) {
                document.getElementById('img_theoretical').src = `/images/theoretical_limits.png?t=${t}`;
            }
            alert('Simülasyon başarıyla tamamlandı!');
            loadHistory(); // Listeyi güncelle
        }
    }

    async function detailView(simId) {
        const res = await fetch(`/api/history/${simId}`);
        const data = await res.json();
        const t = new Date().getTime();
        
        // Dashboard'u eski verilerle doldur
        document.getElementById('stat_bins').innerText = data.stats.num_bins;
        document.getElementById('stat_pdr').innerText = data.stats.pdr + '%';
        
        document.getElementById('img_map').src = `/history-images/${simId}/city_map_sf_distribution.png`;
        document.getElementById('img_heatmap').src = `/history-images/${simId}/coverage_heatmap.png`;
        document.getElementById('img_neighborhood').src = `/history-images/${simId}/neighborhood_analysis.png`;
        document.getElementById('img_pdr').src = `/history-images/${simId}/network_pdr_analysis.png`;
        
        if (document.getElementById('img_device_type')) {
            document.getElementById('img_device_type').src = `/history-images/${simId}/device_type_analysis.png`;
        }
        if (document.getElementById('img_academic')) {
            document.getElementById('img_academic').src = `/history-images/${simId}/academic_constraints.png`;
        }
        
        alert(`${simId} detayları yüklendi.`);
    }

    // --- RAPOR EXPORT ---
    const exportBtn = document.getElementById('export_report_btn');
    if (exportBtn) {
        exportBtn.onclick = () => {
            // Navbar ve Sidebar'ı gizle, sadece ana içeriği yazdır
            window.print();
        };
    }

    runBtn.addEventListener('click', async () => {
        await runSimulation('/api/run-simulation', runBtn, 'TEMEL SİMÜLASYONU BAŞLAT', false);
    });

    if (runFullBtn) {
        runFullBtn.addEventListener('click', async () => {
            await runSimulation('/api/run-simulation', runFullBtn, '🚀 TAM ANALİZİ BAŞLAT', true);
        });
    }

    // --- GEÇMİŞ SİSTEMİ (NEW) ---
    async function loadHistory() {
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            const historyList = document.getElementById('history_list');
            
            if (data.length === 0) return;

            historyList.innerHTML = '';
            data.forEach(item => {
                const div = document.createElement('div');
                div.className = 'card history-item';
                div.style.padding = '10px';
                div.style.fontSize = '0.75rem';
                div.style.cursor = 'pointer';
                div.style.border = '1px solid var(--border)';
                div.style.transition = '0.2s';
                div.innerHTML = `
                    <div style="font-weight: bold; color: var(--primary);">${item.date}</div>
                    <div style="color: var(--text-muted); margin-top: 4px;">PDR: %${item.pdr} | Cihaz: ${item.devices}</div>
                `;
                div.onclick = () => renderHistory(item.id);
                historyList.appendChild(div);
            });
        } catch (err) {
            console.error('History load error:', err);
        }
    }

    async function renderHistory(simId) {
        try {
            const response = await fetch(`/api/history/${simId}`);
            const data = await response.json();
            
            // Verileri Güncelle (Güvenli Kontrol)
            const setVal = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.innerText = val;
            };

            setVal('stat_bins', data.stats.num_bins.toLocaleString());
            setVal('stat_pdr', data.stats.pdr + '%');
            setVal('stat_blindness', data.stats.blindness);

            // Tasarruf Yeniden Hesapla (Arşiv için)
            if (document.getElementById('stat_savings')) {
                const baseSavingPerBin = 650;
                const totalSaving = Math.round(data.stats.num_bins * (data.stats.pdr / 100) * baseSavingPerBin);
                document.getElementById('stat_savings').innerText = `₺${(totalSaving/1000).toFixed(1)}K`;
            }
            
            // Grafikleri Geçmişten Yükle (Güvenli Kontrol)
            const t = new Date().getTime();
            const setImg = (id, filename) => {
                const el = document.getElementById(id);
                if (el) el.src = `/history-images/${simId}/${filename}?t=${t}`;
            };

            setImg('img_map', 'city_map_sf_distribution.png');
            setImg('img_heatmap', 'coverage_heatmap.png');
            setImg('img_neighborhood', 'neighborhood_analysis.png');
            setImg('img_pdr', 'network_pdr_analysis.png');
            setImg('img_energy', 'energy_analysis.png');
            setImg('img_signal', 'signal_quality.png');
            
            // Konsolu Temizle ve Bilgi Ver
            const logWindow = document.getElementById('sim_logs');
            if (logWindow) {
                logWindow.innerHTML = `<div style="color: #60a5fa;">> [ARŞİV] ${simId} tarihli belediye raporu yüklendi.</div>`;
            }
            
            alert(`${simId} tarihli belediye arşivi başarıyla yüklendi.`);
        } catch (err) {
            console.error('Render history error:', err);
            alert('Arşiv yüklenirken bir hata oluştu. Veri yapısı uyumsuz olabilir.');
        }
    }

    // Başlangıçta yükle
    loadHistory();
    // ----------------------------

    // Kart Giriş Animasyonu
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = '0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});
