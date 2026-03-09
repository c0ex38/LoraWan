import math
from . import config

def calculate_time_on_air(payload_size, sf, bw=config.DEFAULT_BW, cr=config.DEFAULT_CR, preamble_len=config.PREAMBLE_LEN, header_disabled=False, low_dr_optimize=None):
    """
    LoRaWAN paketinin havada kalma süresini (ToA) hesaplar.
    """
    bw_hz = bw * 1000
    t_sym = (2**sf) / bw_hz
    t_preamble = (preamble_len + 4.25) * t_sym
    
    if low_dr_optimize is None:
        de = 1 if (sf >= 11 and bw <= 125) else 0
    else:
        de = 1 if low_dr_optimize else 0
        
    h = 1 if header_disabled else 0
    crc = 1 
    
    term1 = 8 * payload_size - 4 * sf + 28 + 16 * crc - 20 * h
    term2 = 4 * (sf - 2 * de)
    
    n_payload_val = 8 + max(math.ceil(term1 / term2) * (cr + 4), 0)
    t_payload = n_payload_val * t_sym
    
    return (t_preamble + t_payload) * 1000

def calculate_energy_consumption(toa_ms, tx_current_ma=config.TX_CURRENT_MA, voltage=config.OPERATING_VOLTAGE):
    """Harcanan enerjiyi (miliJoule) hesaplar."""
    time_s = toa_ms / 1000
    return voltage * tx_current_ma * time_s

def calculate_bit_rate(sf, bw=config.DEFAULT_BW, cr=config.DEFAULT_CR):
    """LoRa fiziksel katman bit hızını hesaplar (bps)."""
    bw_hz = bw * 1000
    return sf * (bw_hz / (2**sf)) * (4 / (4 + cr))

def check_collision_sir(p1_sf, p2_sf, p1_rssi, p2_rssi):
    """SIR ve Capture Effect Analizi."""
    sir = p1_rssi - p2_rssi
    
    if p1_sf == p2_sf:
        return sir >= config.CAPTURE_EFFECT_THRESHOLD
    
    threshold = config.REJECTION_MATRIX.get(p1_sf, {}).get(p2_sf, -20)
    return sir >= threshold

def calculate_path_loss(distance_m, f_mhz=868, n=config.PATH_LOSS_EXPONENT, d0=1.0, pl0=14.7):
    """Log-Distance Path Loss Modeli."""
    dist = max(distance_m, d0)
    return pl0 + 10 * n * math.log10(dist / d0)

def get_sf_sensitivity(sf, bw=config.DEFAULT_BW):
    """SF bazlı tipik LoRa duyarlılık değerleri (dBm)."""
    return config.SF_SENSITIVITY.get(sf, -120)

def get_required_snr(sf):
    """Kayıpsız iletişim için gereken minimum SNR (dB)."""
    return config.REQUIRED_SNR.get(sf, -5)

def calculate_duty_cycle_off_time(toa_ms, duty_cycle_limit=config.DUTY_CYCLE_LIMIT):
    """Duty Cycle kısıtına göre sessizlik süresi."""
    t_on = toa_ms / 1000
    return (t_on / duty_cycle_limit) - t_on

def get_mtu_limit(sf):
    """EU868 standartlarına göre SF bazlı Maksimum Payload (MTU)."""
    return config.MTU_LIMITS.get(sf, 51)

def calculate_link_margin(current_snr, sf):
    """Link Margin = Current SNR - Required SNR"""
    return current_snr - get_required_snr(sf)

def calculate_noise_floor(bw=config.DEFAULT_BW, noise_figure=6):
    """Termal Gürültü Tabanı (Noise Floor) Hesabı."""
    bw_hz = bw * 1000
    return -174 + 10 * math.log10(bw_hz) + noise_figure
