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
    runBtn.addEventListener('click', async () => {
        const config = {
            num_bins: document.getElementById('num_bins').value,
            num_gateways: document.getElementById('num_gateways').value,
            area_size: document.getElementById('area_size').value
        };

        // UI Durumu: Loading
        runBtn.disabled = true;
        runBtn.innerText = 'SIMULATING...';
        runBtn.style.opacity = '0.5';

        try {
            const response = await fetch('/api/run-simulation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            const data = await response.json();

            if (data.status === 'success') {
                // KPI Değerlerini Güncelle
                document.getElementById('stat_bins').innerText = data.stats.num_bins.toLocaleString();
                document.getElementById('stat_gateways').innerText = data.stats.num_gateways;
                document.getElementById('stat_pdr').innerText = data.stats.pdr + '%';
                document.getElementById('stat_blindness').innerText = data.stats.blindness;

                // Grafikleri Yenile (Cache önlemek için timestamp ekle)
                const t = new Date().getTime();
                document.getElementById('img_map').src = `/images/city_map_sf_distribution.png?t=${t}`;
                document.getElementById('img_pdr').src = `/images/network_pdr_analysis.png?t=${t}`;
                document.getElementById('img_energy').src = `/images/energy_analysis.png?t=${t}`;
                document.getElementById('img_signal').src = `/images/signal_quality.png?t=${t}`;

                alert('Simulation completed successfully!');
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('An error occurred during simulation.');
        } finally {
            runBtn.disabled = false;
            runBtn.innerText = 'RUN SIMULATION';
            runBtn.style.opacity = '1';
        }
    });

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
