# Mapping kode saham IDX → Yahoo Finance format (.JK suffix)

IDX_TICKERS = {
    # Perbankan
    "BBCA": "BBCA.JK",
    "BBRI": "BBRI.JK",
    "BMRI": "BMRI.JK",
    "BBNI": "BBNI.JK",
    "BRIS": "BRIS.JK",
    "MEGA": "MEGA.JK",
    "NISP": "NISP.JK",

    # Telekomunikasi
    "TLKM": "TLKM.JK",
    "EXCL": "EXCL.JK",
    "ISAT": "ISAT.JK",

    # Energi & Tambang
    "ADRO": "ADRO.JK",
    "PTBA": "PTBA.JK",
    "ITMG": "ITMG.JK",
    "INCO": "INCO.JK",
    "MEDC": "MEDC.JK",
    "ANTM": "ANTM.JK",
    "TINS": "TINS.JK",

    # Consumer & Retail
    "UNVR": "UNVR.JK",
    "ICBP": "ICBP.JK",
    "INDF": "INDF.JK",
    "MAPI": "MAPI.JK",
    "ACES": "ACES.JK",

    # Infrastruktur & Konstruksi
    "WIKA": "WIKA.JK",
    "WSKT": "WSKT.JK",
    "PTPP": "PTPP.JK",
    "JSMR": "JSMR.JK",

    # Properti
    "BSDE": "BSDE.JK",
    "CTRA": "CTRA.JK",
    "LPKR": "LPKR.JK",
    "SMRA": "SMRA.JK",

    # Diversified
    "ASII": "ASII.JK",
    "HMSP": "HMSP.JK",
    "GGRM": "GGRM.JK",

    # Tech
    "EMTK": "EMTK.JK",
    "GOTO": "GOTO.JK",
    "BUKA": "BUKA.JK",
}

# Indeks IDX
IDX_INDICES = {
    "IHSG": "^JKSE",
    "LQ45": "^JKLQ45",
    "IDX30": "^JKIDX30",
}

# Pasangan Forex USD (default)
FOREX_PAIRS = {
    "XAU/USD": "GC=F",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CHF": "USDCHF=X",
    "USD/CAD": "USDCAD=X",
    "NZD/USD": "NZDUSD=X",
}


def get_yahoo_ticker(idx_code: str) -> str:
    """Konversi kode IDX ke format Yahoo Finance"""
    code = idx_code.upper()
    if code in IDX_TICKERS:
        return IDX_TICKERS[code]
    # Default: tambahkan .JK suffix
    return f"{code}.JK"


def get_all_idx_tickers() -> list:
    return list(IDX_TICKERS.values())
