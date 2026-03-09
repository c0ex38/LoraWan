document.addEventListener('DOMContentLoaded', () => {
    // Navigasyon tıklama efektleri
    const navItems = document.querySelectorAll('nav li');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            // Smoot scroll simülasyonu veya bölüm değiştirme eklenebilir
            console.log(`Navigating to: ${item.innerText}`);
        });
    });

    // KPI Kartlarına basit bir giriş animasyonu
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

    // İmaj yüklenememe durumunda bir "placeholder" gösterimi ekleyebiliriz
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.onerror = function() {
            this.src = 'https://via.placeholder.com/800x600/1e293b/94a3b8?text=Simulasyon+Gorseli+Hazirlaniyor';
        };
    });
});
