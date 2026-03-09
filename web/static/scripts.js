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
                    full_suite: isFull
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
            const baseSavingPerBin = 420; // TL
            const totalSaving = Math.round(data.stats.num_bins * (data.stats.pdr / 100) * baseSavingPerBin);
            document.getElementById('stat_savings').innerText = `₺${(totalSaving/1000).toFixed(1)}K`;
            
            document.getElementById('stat_pdr').innerText = data.stats.pdr + '%';
            document.getElementById('stat_blindness').innerText = data.stats.blindness;

            const t = new Date().getTime();
            document.getElementById('img_map').src = `/images/city_map_sf_distribution.png?t=${t}`;
            document.getElementById('img_pdr').src = `/images/network_pdr_analysis.png?t=${t}`;
            document.getElementById('img_energy').src = `/images/energy_analysis.png?t=${t}`;
            document.getElementById('img_signal').src = `/images/signal_quality.png?t=${t}`;
            
            if (document.getElementById('img_theoretical')) {
                document.getElementById('img_theoretical').src = `/images/theoretical_limits.png?t=${t}`;
            }
            alert('Simülasyon başarıyla tamamlandı!');
            loadHistory(); // Listeyi güncelle
        }
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
            
            // Verileri Güncelle
            document.getElementById('stat_bins').innerText = data.stats.num_bins.toLocaleString();
            document.getElementById('stat_gateways').innerText = data.stats.num_gateways;
            document.getElementById('stat_pdr').innerText = data.stats.pdr + '%';
            document.getElementById('stat_blindness').innerText = data.stats.blindness;

            // Grafikleri Geçmişten Yükle
            const t = new Date().getTime();
            document.getElementById('img_map').src = `/history-images/${simId}/city_map_sf_distribution.png?t=${t}`;
            document.getElementById('img_pdr').src = `/history-images/${simId}/network_pdr_analysis.png?t=${t}`;
            document.getElementById('img_energy').src = `/history-images/${simId}/energy_analysis.png?t=${t}`;
            document.getElementById('img_signal').src = `/history-images/${simId}/signal_quality.png?t=${t}`;
            
            // Konsolu Temizle ve Bilgi Ver
            const logWindow = document.getElementById('sim_logs');
            logWindow.innerHTML = `> [ARŞİV] ${simId} tarihli simülasyon verileri yüklendi.`;
            
            alert(`${simId} tarihli arşiv yüklendi.`);
        } catch (err) {
            alert('Arşiv yüklenirken bir hata oluştu.');
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
