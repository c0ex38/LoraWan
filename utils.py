import math

def calculate_time_on_air(payload_size, sf, bw=125, cr=1, preamble_len=8, header_disabled=False, low_dr_optimize=None):
    """
    LoRaWAN paketinin havada kalma süresini (ToA) hesaplar.
    
    Args:
        payload_size (int): Byte cinsinden veri yükü
        sf (int): Spreading Factor (7-12)
        bw (float): Bandwidth (kHz cinsinden, varsayılan 125)
        cr (int): Coding Rate (1: 4/5, 2: 4/6, 3: 4/7, 4: 4/8)
        preamble_len (int): Preamble sembol sayısı (varsayılan 8)
    
    Returns:
        float: Milisaniye cinsinden toplam süre
    """
    
    # BW'yi Hz'e çevir
    bw_hz = bw * 1000
    
    # Sembol süresi (T_s)
    # T_s = (2^SF) / BW
    t_sym = (2**sf) / bw_hz
    
    # Preamble süresi
    t_preamble = (preamble_len + 4.25) * t_sym
    
    # Payload sembol sayısı (n_payload)
    # Formül: 8 + max(ceil((8PL - 4SF + 28 + 16CRC - 20H) / (4(SF - 2DE))) * (CR + 4), 0)
    
    # Low Data Rate Optimization (DE)
    # SF11 ve SF12'de BW 125kHz ise genellikle zorunludur.
    if low_dr_optimize is None:
        de = 1 if (sf >= 11 and bw <= 125) else 0
    else:
        de = 1 if low_dr_optimize else 0
        
    h = 1 if header_disabled else 0
    crc = 1 # LoRaWAN uplink paketlerinde CRC aktiftir
    
    term1 = 8 * payload_size - 4 * sf + 28 + 16 * crc - 20 * h
    term2 = 4 * (sf - 2 * de)
    
    n_payload_val = 8 + max(math.ceil(term1 / term2) * (cr + 4), 0)
    
    t_payload = n_payload_val * t_sym
    
    # Toplam süre (ms)
    return (t_preamble + t_payload) * 1000

def calculate_energy_consumption(toa_ms, tx_current_ma=120, voltage=3.3):
    """
    Bir paket iletimi için harcanan enerjiyi (miliJoule) hesaplar.
    E = V * I * t
    """
    time_s = toa_ms / 1000
    energy_mj = voltage * tx_current_ma * time_s
    return energy_mj

def calculate_bit_rate(sf, bw=125, cr=1):
    """
    LoRa fiziksel katman bit hızını hesaplar (bps).
    R_b = SF * (BW / 2^SF) * (4 / (4 + CR))
    """
    bw_hz = bw * 1000
    r_b = sf * (bw_hz / (2**sf)) * (4 / (4 + cr))
    return r_b

def calculate_collision_probability(num_devices, toa_ms, interval_s):
    """
    Basit bir ALOHA tabanlı çakışma olasılığı hesabı.
    P_collision = 1 - e^(-2 * G)
    G = (Cihaz Sayısı * ToA) / İletim Aralığı
    """
    toa_s = toa_ms / 1000
    g = (num_devices * toa_s) / interval_s
    prob = 1 - math.exp(-2 * g)
    return prob

def check_collision_sir(p1_sf, p2_sf, p1_rssi, p2_rssi):
    """
    LoRa SIR (Signal-to-Interference Ratio) tabanlı çakışma kontrolü.
    Farklı SF'ler birbirine karşı belirli bir koruma sağlar (Orthogonality).
    """
    # SIR Thresholds (dB) - Ortak LoRa modellerinden alınmıştır
    # Aynı SF çakışması için ~6dB fark gerekir.
    sir_thresholds = {
        (7, 7): 6, (8, 8): 6, (9, 9): 6, (10, 10): 6, (11, 11): 6, (12, 12): 6,
        # Farklı SF'ler arası (örnek değerler)
        (7, 8): -16, (7, 9): -18, (7, 10): -20,
        (8, 7): -16, (8, 9): -16, (9, 7): -18
    }
    
    threshold = sir_thresholds.get((p1_sf, p2_sf), -20)
    sir = p1_rssi - p2_rssi
    
    # SIR threshold'dan büyükse p1 hayatta kalır
    return sir > threshold

def calculate_path_loss(distance_m, f_mhz=868, n=3.0, d0=1.0, pl0=14.7):
    """
    Log-Distance Path Loss Modeli.
    PL = PL0 + 10 * n * log10(d/d0) + Shadowing
    """
    # Mesafe 0 olamaz
    dist = max(distance_m, d0)
    path_loss = pl0 + 10 * n * math.log10(dist / d0)
    return path_loss

def get_sf_sensitivity(sf, bw=125):
    """
    SF bazlı tipik LoRa duyarlılık değerleri (dBm).
    (SX1276 datasheet bazlı yaklaşık değerler)
    """
    sensitivities = {
        7: -123,
        8: -126,
        9: -129,
        10: -132,
        11: -134.5,
        12: -137
    }
    return sensitivities.get(sf, -120)

def get_required_snr(sf):
    """
    Kayıpsız iletişim için gereken minimum SNR (dB).
    """
    snr_table = {
        7: -7.5,
        8: -10,
        9: -12.5,
        10: -15,
        11: -17.5,
        12: -20
    }
    return snr_table.get(sf, -5)
