"""Stock universe definitions for screening.

Primary focus: Indian NSE market with Nifty indices.
Also includes legacy US/UK/EU markets for backward compatibility.
"""

import logging

logger = logging.getLogger(__name__)

# ── NSE India Universes (primary) ──────────────────────────────────
# These are sourced from the NSE data module, with hardcoded fallback
# and periodic API refresh capability.

from data.nse_sources import get_nse_constituents

_NSE_CACHE = None


def _get_nse_indices() -> dict[str, list[str]]:
    """Get NSE index constituents (cached)."""
    global _NSE_CACHE
    if _NSE_CACHE is None:
        _NSE_CACHE = get_nse_constituents()
    return _NSE_CACHE


def get_nse_universe(name: str) -> list[str]:
    """Get an NSE index universe by name.

    Args:
        name: One of 'nifty50', 'nifty_next50', 'nifty200', 'nifty500',
              'nifty_midcap150', 'nifty_smallcap250', 'nifty_midsml400',
              'nifty_bank'

    Returns:
        List of ticker symbols with .NS suffix, or empty list if not found.
    """
    indices = _get_nse_indices()
    return indices.get(name, [])


# ── US Markets (legacy) ────────────────────────────────────────────
SP500_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "BRK.B", "BRK.A",
    "LLY", "V", "AVGO", "JPM", "TSLA", "WMT", "XOM", "UNH", "MA", "PG",
    "JNJ", "COST", "ORCL", "HD", "BAC", "CVX", "NFLX", "ABBV", "MRK",
    "CRM", "KO", "ADBE", "PEP", "AMD", "DIS", "TMO", "WFC", "CSCO", "ABT",
    "MCD", "GE", "LIN", "TMUS", "TXN", "QCOM", "IBM", "ACN", "INTU",
]

NASDAQ100_TICKERS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "GOOG", "TSLA", "AVGO",
    "COST", "NFLX", "ADBE", "AMD", "PEP", "QCOM", "TXN", "AMGN", "INTU",
    "TMUS", "ISRG", "BKNG", "CMCSA", "HON", "SBUX", "MDLZ", "ADI", "GILD",
]

WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD",
    "NFLX", "COST", "CRM", "ADBE", "QCOM", "MU", "INTC", "DIS",
    "BA", "CAT", "GE", "JPM", "GS", "PYPL", "SNAP", "UBER",
    "PLTR", "SOFI", "RIVN", "LCID", "MARA", "COIN", "MSTR",
]

# ── India NSE (legacy direct lists) ────────────────────────────────
NSE_NIFTY50_TICKERS = get_nse_universe("nifty50")
NSE_NEXT50_TICKERS = get_nse_universe("nifty_next50")
NSE_BANK_TICKERS = [
    "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "AXISBANK.NS",
    "INDUSINDBK.NS", "BANKBARODA.NS", "FEDERALBNK.NS", "PNB.NS", "CANBK.NS",
    "IDFCFIRSTB.NS", "BANDHANBNK.NS", "YESBANK.NS", "RBLBANK.NS", "AUBANK.NS",
    "KARURVYSYA.NS", "CUB.NS", "SOUTHBANK.NS", "DCBBANK.NS", "IDBI.NS",
]

# ── UK LSE (legacy) ────────────────────────────────────────────────
FTSE100_TICKERS = [
    "HSBA.L", "BP.L", "SHEL.L", "GSK.L", "AZN.L", "DGE.L", "ULVR.L", "RIO.L",
    "BARC.L", "LLOY.L", "PRU.L", "VOD.L", "GLEN.L", "NG.L", "REL.L",
    "BT-A.L", "SSE.L", "ITRK.L", "IMB.L", "SGRO.L", "AHT.L", "ABF.L",
    "ADM.L", "ANTO.L", "AUTO.L", "AV.L", "BA.L", "BDEV.L", "BKG.L",
    "BNZL.L", "BRBY.L", "CCH.L", "CNA.L", "CPG.L", "CRDA.L", "CTEC.L",
    "DCC.L", "DC.L", "EXPN.L", "EZJ.L", "FLTR.L", "FRES.L", "GFS.L",
    "GLEN.L", "GSK.L", "HIK.L", "HL.L", "HLMA.L", "HWDN.L", "IAG.L",
    "ICG.L", "IHG.L", "III.L", "IMI.L", "INF.L", "INT.L", "ISPY.L",
    "JMAT.L", "KGF.L", "LAND.L", "LGEN.L", "LMP.L", "LSEG.L", "MNG.L",
    "MRO.L", "MNDI.L", "MKS.L", "MRW.L", "NXT.L", "OCDO.L", "PSN.L",
    "PSON.L", "PZC.L", "RTO.L", "SBRY.L", "SDR.L", "SGE.L", "SMT.L",
    "SMIN.L", "SN.L", "SPX.L", "STAN.L", "STJ.L", "SVT.L", "TSCO.L",
    "TUI.L", "TW.L", "UKCM.L", "UU.L", "VTY.L", "WEIR.L", "WPP.L",
    "WTB.L", "XAR.L",
]

# ── Europe (legacy) ────────────────────────────────────────────────
EURO50_TICKERS = [
    "SAP.DE", "AIR.PA", "MC.PA", "OR.PA", "SIE.DE", "ALV.DE", "BN.PA",
    "BMW.DE", "VOW3.DE", "BAS.DE", "BAYN.DE", "ADS.DE", "DBK.DE", "DHER.DE",
    "DTE.DE", "EOAN.DE", "FRE.DE", "HEI.DE", "HEN3.DE", "IFX.DE",
    "LIN.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "PUM.DE", "QIA.DE",
    "RWE.DE", "SY1.DE", "VNA.DE", "ZAL.DE",
    "AC.PA", "AI.PA", "CS.PA", "DG.PA", "DSY.PA", "EL.PA",
    "EN.PA", "GLE.PA", "KER.PA", "LR.PA", "ML.PA", "POM.PA",
    "RF.PA", "RI.PA", "RMS.PA", "SU.PA", "SW.PA", "TTE.PA",
    "VIE.PA", "VIV.PA",
]


def get_universe(name: str = "nifty50") -> list[str]:
    """Get a predefined stock universe by name.

    Default is Nifty 50. Available universes:

    NSE India (primary):
        - nifty50, nifty_next50, nifty200, nifty500
        - nifty_midcap150, nifty_smallcap250, nifty_midsml400
        - nifty_bank

    Legacy:
        - sp500, nasdaq100, watchlist
        - ftse100, euro50
    """
    # Build universes dict dynamically to include NSE indices
    nse = _get_nse_indices()
    universes = {
        # NSE India
        **nse,
        "nse_nifty50": nse.get("nifty50", NSE_NIFTY50_TICKERS),
        "nse_next50": nse.get("nifty_next50", NSE_NEXT50_TICKERS),
        "nse_bank": nse.get("nifty_bank", NSE_BANK_TICKERS),
        # US legacy
        "sp500": SP500_TICKERS,
        "nasdaq100": NASDAQ100_TICKERS,
        "watchlist": WATCHLIST,
        # UK/EU legacy
        "ftse100": FTSE100_TICKERS,
        "euro50": EURO50_TICKERS,
    }
    return universes.get(name.lower(), nse.get("nifty50", NSE_NIFTY50_TICKERS))
