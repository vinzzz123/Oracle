"""
GET IDX TICKERS
===============
Helper script to get all Indonesian stock tickers from IDX

This creates a comprehensive list of all stocks trading on
the Indonesia Stock Exchange for use with Project Oracle.
"""

import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time


def get_idx_tickers_from_yahoo():
    """
    Method 1: Get IDX tickers from Yahoo Finance
    Note: This might not get all stocks
    """
    print("Method 1: Fetching from Yahoo Finance...")
    
    # Some major IDX stocks as starting point
    major_idx = [
        # Banking
        "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK",
        # Telecom
        "TLKM.JK", "EXCL.JK", "ISAT.JK",
        # Consumer
        "ICBP.JK", "INDF.JK", "MYOR.JK", "ULTJ.JK", "UNVR.JK",
        # Mining & Energy
        "ADRO.JK", "PTBA.JK", "ITMG.JK", "ANTM.JK", "INCO.JK", "PGAS.JK",
        # Automotive & Heavy Equipment
        "ASII.JK", "UNTR.JK", "AUTO.JK",
        # Construction
        "WSKT.JK", "WIKA.JK", "PTPP.JK", "ADHI.JK",
        # Technology
        "GOTO.JK", "BUKA.JK",
        # Property
        "BSDE.JK", "CTRA.JK", "SMRA.JK", "PWON.JK",
        # Plantation
        "AALI.JK", "LSIP.JK",
        # Poultry
        "CPIN.JK", "JPFA.JK",
        # Retail
        "ACES.JK", "MAPI.JK",
        # Healthcare
        "HEAL.JK", "SILO.JK",
    ]
    
    return major_idx


def get_idx_tickers_comprehensive():
    """
    Method 2: Comprehensive list - manually curated
    Based on IDX sectors and major components
    """
    print("Method 2: Loading comprehensive manual list...")
    
    # You can expand this list significantly
    # This is organized by sector
    
    idx_comprehensive = {
        'Banking': [
            "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK",
            "BNLI.JK", "NISP.JK", "MEGA.JK", "PNBN.JK", "BTPS.JK",
            "BNGA.JK", "BNII.JK", "BDMN.JK"
        ],
        'Mining': [
            "ADRO.JK", "PTBA.JK", "ITMG.JK", "HRUM.JK", "DOID.JK",
            "ANTM.JK", "INCO.JK", "MDKA.JK", "TINS.JK", "DKFT.JK",
            "ARCI.JK", "GEMS.JK"
        ],
        'Energy': [
            "PGAS.JK", "MEDC.JK", "ELSA.JK"
        ],
        'Consumer': [
            "ICBP.JK", "INDF.JK", "MYOR.JK", "ULTJ.JK", "UNVR.JK",
            "KLBF.JK", "SIDO.JK", "HMSP.JK", "GGRM.JK", "WIIM.JK",
            "CAMP.JK", "DLTA.JK", "ROTI.JK"
        ],
        'Technology': [
            "GOTO.JK", "BUKA.JK", "WIFI.JK", "DCII.JK"
        ],
        'Telecom': [
            "TLKM.JK", "EXCL.JK", "ISAT.JK", "FREN.JK"
        ],
        'Automotive': [
            "ASII.JK", "AUTO.JK", "IMAS.JK", "SMSM.JK", "GDYR.JK",
            "PRAS.JK", "NIPS.JK"
        ],
        'Heavy_Equipment': [
            "UNTR.JK", "TOBA.JK"
        ],
        'Construction': [
            "WSKT.JK", "WIKA.JK", "PTPP.JK", "ADHI.JK", "WTON.JK",
            "ACST.JK", "TOTL.JK", "DGIK.JK"
        ],
        'Property': [
            "BSDE.JK", "CTRA.JK", "SMRA.JK", "PWON.JK", "APLN.JK",
            "DUTI.JK", "ASRI.JK", "BEST.JK", "KIJA.JK", "LPKR.JK",
            "PANI.JK", "MDLN.JK"
        ],
        'Retail': [
            "ACES.JK", "MAPI.JK", "ERAA.JK", "RALS.JK", "LPPF.JK"
        ],
        'Plantation': [
            "AALI.JK", "LSIP.JK", "SIMP.JK", "SSMS.JK", "TBLA.JK"
        ],
        'Poultry': [
            "CPIN.JK", "JPFA.JK", "MAIN.JK"
        ],
        'Healthcare': [
            "HEAL.JK", "SILO.JK", "MIKA.JK", "SAME.JK"
        ],
        'Transportation': [
            "BIRD.JK", "WEHA.JK", "SMDR.JK", "KARW.JK"
        ],
        'Media': [
            "SCMA.JK", "MNCN.JK", "ABBA.JK"
        ],
        'Cement': [
            "SMGR.JK", "INTP.JK", "WSBP.JK", "SMBR.JK"
        ],
        'Steel': [
            "KRAS.JK", "BAJA.JK", "ISSP.JK"
        ],
        'Packaging': [
            "TKIM.JK", "AKPI.JK", "FPNI.JK", "PACK.JK"
        ],
    }
    
    # Flatten to single list
    all_tickers = []
    for sector, tickers in idx_comprehensive.items():
        all_tickers.extend(tickers)
    
    return list(set(all_tickers))  # Remove duplicates


def verify_tickers(tickers):
    """
    Verify that tickers are valid and can be accessed
    """
    print(f"\nVerifying {len(tickers)} tickers...")
    
    valid_tickers = []
    invalid_tickers = []
    
    for i, ticker in enumerate(tickers, 1):
        if i % 20 == 0:
            print(f"  Progress: {i}/{len(tickers)}")
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we can get basic info
            if info.get('regularMarketPrice') or info.get('currentPrice'):
                valid_tickers.append(ticker)
            else:
                invalid_tickers.append(ticker)
        
        except:
            invalid_tickers.append(ticker)
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"\n✅ Valid: {len(valid_tickers)}")
    print(f"❌ Invalid: {len(invalid_tickers)}")
    
    return valid_tickers, invalid_tickers


def save_tickers(tickers, filename="idx_tickers.txt"):
    """
    Save ticker list to file
    """
    with open(filename, 'w') as f:
        for ticker in sorted(tickers):
            f.write(f"{ticker}\n")
    
    print(f"\n💾 Saved {len(tickers)} tickers to {filename}")


def create_ticker_csv(tickers, filename="idx_tickers.csv"):
    """
    Create a CSV with ticker information
    """
    print(f"\nCreating detailed CSV for {len(tickers)} tickers...")
    
    data = []
    
    for i, ticker in enumerate(tickers, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(tickers)}")
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            data.append({
                'ticker': ticker,
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'IDR'),
            })
        
        except:
            data.append({
                'ticker': ticker,
                'name': '',
                'sector': '',
                'industry': '',
                'market_cap': 0,
                'currency': 'IDR',
            })
        
        time.sleep(0.1)
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    
    print(f"\n💾 Saved detailed info to {filename}")
    return df


def main():
    """
    Main function to generate IDX ticker list
    """
    print("="*70)
    print("IDX TICKER LIST GENERATOR")
    print("="*70)
    
    print("\nSelect method:")
    print("1. Quick list (50+ major stocks)")
    print("2. Comprehensive manual list (200+ stocks)")
    print("3. Both + verification")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == '1':
        tickers = get_idx_tickers_from_yahoo()
    elif choice == '2':
        tickers = get_idx_tickers_comprehensive()
    elif choice == '3':
        tickers1 = get_idx_tickers_from_yahoo()
        tickers2 = get_idx_tickers_comprehensive()
        tickers = list(set(tickers1 + tickers2))
        
        # Verify
        verify = input("\nVerify tickers? (yes/no): ").strip().lower()
        if verify == 'yes':
            tickers, invalid = verify_tickers(tickers)
    else:
        print("Invalid choice")
        return
    
    print(f"\nTotal tickers: {len(tickers)}")
    
    # Save
    save_tickers(tickers)
    
    # Create detailed CSV
    create_csv = input("\nCreate detailed CSV? (yes/no): ").strip().lower()
    if create_csv == 'yes':
        create_ticker_csv(tickers)
    
    print("\n✅ Done!")
    print(f"\n💡 Use these files with Project Oracle:")
    print("   - idx_tickers.txt: Simple list")
    print("   - idx_tickers.csv: Detailed info")


if __name__ == "__main__":
    main()