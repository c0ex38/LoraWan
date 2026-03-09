import math
from . import config

def calculate_time_on_air(payload_size, sf, bw=config.DEFAULT_BW, cr=config.DEFAULT_CR, preamble_len=config.PREAMBLE_LEN, header_disabled=False, low_dr_optimize=None):
    """
    LoRaWAN paketinin havada kalma süresini (ToA) milisaniye cinsinden hesaplar.
    
    Argümanlar:
        payload_size: Byte cinsinden veri miktarı.
        sf: Spreading Factor (7-12).
        bw: Bant genişliği (kHz).
        cr: Kodlama oranı (1..4).
    """
    bw_hz = bw * 1000
    t_sym = (2**sf) / bw_hz # Sembol süresi
    t_preamble = (preamble_len + 4.25) * t_sym # Giriş süresi
    
    # Düşük Veri Hızı Optimizasyonu (SF11-12'de genellikle zorunludur)
    if low_dr_optimize is None:
        de = 1 if (sf >= 11 and bw <= 125) else 0
    else:
        de = 1 if low_dr_optimize else 0
        
    h = 1 if header_disabled else 0
    crc = 1 
    
    # Semtech LoRa Spesifikasyonuna göre payload sembol sayısı formülü
    term1 = 8 * payload_size - 4 * sf + 28 + 16 * crc - 20 * h
    term2 = 4 * (sf - 2 * de)
    
    n_payload_val = 8 + max(math.ceil(term1 / term2) * (cr + 4), 0)
    t_payload = n_payload_val * t_sym
    
    return (t_preamble + t_payload) * 1000 # ms cinsinden sonuç

def calculate_energy_consumption(toa_ms, tx_current_ma=config.TX_CURRENT_MA, voltage=config.OPERATING_VOLTAGE):
    """Bir paket iletiminde harcanan enerjiyi (miliJoule) hesaplar."""
    time_s = toa_ms / 1000
    return voltage * tx_current_ma * time_s

def calculate_bit_rate(sf, bw=config.DEFAULT_BW, cr=config.DEFAULT_CR):
    """LoRa fiziksel katman bit hızını hesaplar (bps)."""
    bw_hz = bw * 1000
    return sf * (bw_hz / (2**sf)) * (4 / (4 + cr))

def check_collision_sir(p1_sf, p2_sf, p1_rssi, p2_rssi):
    """
    İki paket arasındaki Sinyal-Girişim Oranı (SIR) üzerinden çakışma analizi yapar.
    Capture Effect (Yakalama Etkisi) ve Inter-SF Rejection kurallarını uygular.
    """
    sir = p1_rssi - p2_rssi
    
    # Aynı SF: 6dB fark varsa güçlü paket hayatta kalır.
    if p1_sf == p2_sf:
        return sir >= config.CAPTURE_EFFECT_THRESHOLD
    
    # Farklı SF: Rejection matrix üzerinden eşik kontrolü yapılır.
    threshold = config.REJECTION_MATRIX.get(p1_sf, {}).get(p2_sf, -20)
    return sir >= threshold

def calculate_path_loss(distance_m, f_mhz=868, n=config.PATH_LOSS_EXPONENT, d0=1.0, pl0=14.7):
    """Log-Distance Path Loss modeli ile yol kaybını (dB) hesaplar."""
    dist = max(distance_m, d0)
    return pl0 + 10 * n * math.log10(dist / d0)

def get_sf_sensitivity(sf, bw=config.DEFAULT_BW):
    """Her SF kademesi için tipik LoRa duyarlılık sınırlarını (dBm) döndürür."""
    return config.SF_SENSITIVITY.get(sf, -120)

def get_required_snr(sf):
    """Başarılı bir demodülasyon için gereken minimum SNR (dB) değerini döndürür."""
    return config.REQUIRED_SNR.get(sf, -5)

def calculate_duty_cycle_off_time(toa_ms, duty_cycle_limit=config.DUTY_CYCLE_LIMIT):
    """
    Avrupa yasal standartlarına (%1 Duty Cycle) göre iki paket arası 
    beklenmesi gereken minimum 'sessizlik' süresini hesaplar.
    """
    t_on = toa_ms / 1000
    return (t_on / duty_cycle_limit) - t_on

def get_mtu_limit(sf):
    """Bulunulan SF kademesi için izin verilen maksimum paket boyutu (MTU)."""
    return config.MTU_LIMITS.get(sf, 51)

def calculate_link_margin(current_snr, sf):
    """Bağlantı Payı (Link Margin): Sinyalin kopma noktasından ne kadar uzak olduğu (dB)."""
    return current_snr - get_required_snr(sf)

def calculate_noise_floor(bw=config.DEFAULT_BW, noise_figure=6):
    """
    Termal Gürültü Tabanını hesaplar.
    Gürültü artarsa LoRa'nın 'duyma' yeteneği azalır.
    """
    bw_hz = bw * 1000
    return -174 + 10 * math.log10(bw_hz) + noise_figure
