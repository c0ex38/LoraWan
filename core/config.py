# LoRaWAN Simulation Configuration Module

# -- Fiziksel Katman Parametreleri --
DEFAULT_BW = 125  # kHz
DEFAULT_CR = 1    # 4/5
PREAMBLE_LEN = 8

# -- Enerji Parametreleri --
TX_CURRENT_MA = 120.0
SLEEP_CURRENT_UA = 2.0
OPERATING_VOLTAGE = 3.3
BATTERY_CAPACITY_MAH = 2500

# -- Sinyal ve Hassasiyet Eşikleri (SX1276 bazlı) --
SF_SENSITIVITY = {
    7: -123,
    8: -126,
    9: -129,
    10: -132,
    11: -134.5,
    12: -137
}

REQUIRED_SNR = {
    7: -7.5,
    8: -10,
    9: -12.5,
    10: -15,
    11: -17.5,
    12: -20
}

# -- Protokol Kısıtları (EU868) --
DUTY_CYCLE_LIMIT = 0.01  # %1
MTU_LIMITS = {
    7: 222,
    13: 222, # SF7-8
    8: 222,
    9: 115,
    10: 51,
    11: 51,
    12: 51
}

# -- SIR / Rejection Matrix (Inter-SF Interference) --
# Değerler: p1'in hayatta kalması için p2'den ne kadar güçlü olması gerektiği (SIR_req)
REJECTION_MATRIX = {
    7:  {8: -16, 9: -18, 10: -20, 11: -22, 12: -25},
    8:  {7: -16, 9: -16, 10: -18, 11: -20, 12: -22},
    9:  {7: -18, 8: -16, 10: -16, 11: -18, 12: -20},
    10: {7: -20, 8: -18, 9: -16, 11: -16, 12: -18},
    11: {7: -22, 8: -20, 9: -18, 10: -16, 12: -16},
    12: {7: -25, 8: -22, 9: -20, 10: -18, 11: -16}
}

# -- Çakışma ve Capture Effect --
CAPTURE_EFFECT_THRESHOLD = 6.0  # dB

# -- Senaryo Ayarları --
PATH_LOSS_EXPONENT = 3.0
SHADOWING_STD_NORMAL = 6.0
SHADOWING_STD_STORM = 12.0
JAMMER_RADIUS = 500  # metre
JAMMER_POWER_DB = 30 # dB suppression
CHAOS_FAILURE_CHANCE = 0.05 # %5
