"""
MARKET SCANNER - Indonesian Stock Market Analysis
Scans all IDX stocks and generates analysis reports

File: market_scanner.py - FIXED VERSION
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import yfinance as yf
import time
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Optional

# Try to import investpy for getting complete IDX stock list
try:
    import investpy
    HAS_INVESTPY = True
except ImportError:
    HAS_INVESTPY = False
    print("\n⚠️  Warning: 'investpy' not installed. Using hardcoded stock list.")
    print("Install with: pip install investpy")


# ==============================================================================
# STOCK LISTS
# ==============================================================================

# Top 100 Indonesian stocks for quick scanning
MAJOR_IDX_STOCKS = [
    # Banking
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK",
    "BTPS.JK", "MEGA.JK", "BNGA.JK", "BNLI.JK", "NISP.JK",
    
    # Telecommunications
    "TLKM.JK", "ISAT.JK", "EXCL.JK", "FREN.JK",
    
    # Consumer
    "UNVR.JK", "INDF.JK", "ICBP.JK", "MYOR.JK", "HMSP.JK",
    "GGRM.JK", "MLBI.JK", "CPIN.JK", "JPFA.JK", "MAIN.JK",
    
    # Automotive & Components
    "ASII.JK", "AUTO.JK", "IMAS.JK", "INDS.JK", "SMSM.JK",
    "GDYR.JK", "GJTL.JK", "NIPS.JK", "PRAS.JK",
    
    # Retail
    "ACES.JK", "AMRT.JK", "ERAA.JK", "LPPF.JK", "MAPI.JK",
    "RALS.JK", "SONA.JK",
    
    # Property & Real Estate
    "BSDE.JK", "PWON.JK", "SMRA.JK", "CTRA.JK", "DMAS.JK",
    "PLIN.JK", "BEST.JK", "APLN.JK",
    
    # Mining
    "ADRO.JK", "ITMG.JK", "PTBA.JK", "INDY.JK", "HRUM.JK",
    "MBAP.JK", "KKGI.JK", "GEMS.JK",
    
    # Energy
    "MEDC.JK", "PGAS.JK", "ELSA.JK", "RUIS.JK",
    
    # Metals
    "ANTM.JK", "INCO.JK", "TINS.JK", "SMGR.JK", "INTP.JK",
    "WSBP.JK", "SMBR.JK",
    
    # Media & Technology
    "EMTK.JK", "MNCN.JK", "SCMA.JK", "LINK.JK", "BUKA.JK",
    "GOTO.JK", "BELI.JK",
    
    # Healthcare
    "KAEF.JK", "KLBF.JK", "DVLA.JK", "SIDO.JK", "HEAL.JK",
    
    # Transportation
    "BIRD.JK", "BJBR.JK", "GIAA.JK", "JSMR.JK", "TAXI.JK",
    
    # Conglomerates
    "AALI.JK", "LSIP.JK", "SIMP.JK", "TBLA.JK", "SGRO.JK"
]

# Sector classifications
SECTOR_MAPPING = {
    'banking': ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK", 
                "BTPS.JK", "MEGA.JK", "BNGA.JK", "BNLI.JK", "NISP.JK"],
    'telecom': ["TLKM.JK", "ISAT.JK", "EXCL.JK", "FREN.JK"],
    'consumer': ["UNVR.JK", "INDF.JK", "ICBP.JK", "MYOR.JK", "HMSP.JK", 
                 "GGRM.JK", "MLBI.JK", "CPIN.JK", "JPFA.JK", "MAIN.JK"],
    'automotive': ["ASII.JK", "AUTO.JK", "IMAS.JK", "INDS.JK", "SMSM.JK"],
    'mining': ["ADRO.JK", "ITMG.JK", "PTBA.JK", "INDY.JK", "HRUM.JK", 
               "MBAP.JK", "KKGI.JK", "GEMS.JK"],
    'property': ["BSDE.JK", "PWON.JK", "SMRA.JK", "CTRA.JK", "DMAS.JK", 
                 "PLIN.JK", "BEST.JK", "APLN.JK"],
    'energy': ["MEDC.JK", "PGAS.JK", "ELSA.JK", "RUIS.JK"],
    'retail': ["ACES.JK", "AMRT.JK", "ERAA.JK", "LPPF.JK", "MAPI.JK"],
    'healthcare': ["KAEF.JK", "KLBF.JK", "DVLA.JK", "SIDO.JK", "HEAL.JK"],
    'technology': ["EMTK.JK", "MNCN.JK", "SCMA.JK", "LINK.JK", "BUKA.JK", 
                   "GOTO.JK", "BELI.JK"]
}


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_all_idx_stocks() -> List[str]:
    """Get complete list of all IDX stocks"""
    
    if HAS_INVESTPY:
        try:
            print("📥 Fetching complete IDX stock list from investpy...")
            stocks_df = investpy.stocks.get_stocks(country='indonesia')
            tickers = [f"{symbol}.JK" for symbol in stocks_df['symbol'].tolist()]
            print(f"✅ Found {len(tickers)} stocks")
            return tickers
        except Exception as e:
            print(f"⚠️  Error fetching from investpy: {e}")
            print("Using major stocks list instead...")
    
    return MAJOR_IDX_STOCKS


def get_sector_stocks(sector: str) -> List[str]:
    """Get stocks for a specific sector"""
    sector_lower = sector.lower()
    
    if sector_lower in SECTOR_MAPPING:
        return SECTOR_MAPPING[sector_lower]
    else:
        print(f"❌ Sector '{sector}' not found.")
        print(f"Available sectors: {', '.join(SECTOR_MAPPING.keys())}")
        return []


# ==============================================================================
# SIMPLIFIED ANALYSIS (FAST MODE)
# ==============================================================================

def analyze_stock_simplified(ticker: str) -> Dict:
    """
    Fast analysis for market scanning
    Returns basic metrics and signals
    """
    
    try:
        stock = yf.Ticker(ticker)
        
        # Get basic data
        hist = stock.history(period="6mo")
        info = stock.info
        
        if hist.empty:
            return None
        
        # Current price
        current_price = hist['Close'].iloc[-1]
        
        # Calculate simple metrics
        returns_1m = (hist['Close'].iloc[-1] / hist['Close'].iloc[-20] - 1) * 100 if len(hist) >= 20 else 0
        returns_3m = (hist['Close'].iloc[-1] / hist['Close'].iloc[-60] - 1) * 100 if len(hist) >= 60 else 0
        
        # Simple RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1] if not rsi.empty else 50
        
        # Simple signal
        if current_rsi < 30 and returns_1m < -10:
            signal = "BUY"
            score = 70
        elif current_rsi > 70 and returns_1m > 10:
            signal = "SELL"
            score = 30
        elif 40 < current_rsi < 60:
            signal = "HOLD"
            score = 50
        elif current_rsi < 40:
            signal = "BUY"
            score = 60
        else:
            signal = "HOLD"
            score = 50
        
        return {
            'ticker': ticker,
            'name': info.get('longName', ticker),
            'sector': info.get('sector', 'N/A'),
            'current_price': round(current_price, 2),
            'returns_1m': round(returns_1m, 2),
            'returns_3m': round(returns_3m, 2),
            'rsi': round(current_rsi, 2),
            'signal': signal,
            'score': score,
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', None)
        }
        
    except Exception as e:
        print(f"  ❌ Error analyzing {ticker}: {str(e)}")
        return None


# ==============================================================================
# MARKET SCANNING FUNCTIONS
# ==============================================================================

def quick_scan(limit: int = 100) -> pd.DataFrame:
    """Quick scan of major Indonesian stocks"""
    
    print("\n" + "="*80)
    print("🔍 QUICK MARKET SCAN - Top Indonesian Stocks")
    print("="*80)
    
    stocks = MAJOR_IDX_STOCKS[:limit]
    results = []
    
    print(f"\n📊 Analyzing {len(stocks)} stocks...")
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    for i, ticker in enumerate(stocks, 1):
        print(f"  [{i}/{len(stocks)}] Analyzing {ticker}...", end='\r')
        
        result = analyze_stock_simplified(ticker)
        if result:
            results.append(result)
        
        time.sleep(0.5)
    
    print(f"\n✅ Completed at: {datetime.now().strftime('%H:%M:%S')}")
    
    df = pd.DataFrame(results)
    return df


def full_market_scan() -> pd.DataFrame:
    """Full market scan of all IDX stocks"""
    
    print("\n" + "="*80)
    print("🔍 FULL MARKET SCAN - All IDX Stocks")
    print("="*80)
    
    stocks = get_all_idx_stocks()
    results = []
    
    print(f"\n📊 Analyzing {len(stocks)} stocks...")
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("⏱️  Estimated time: 20-30 minutes")
    
    for i, ticker in enumerate(stocks, 1):
        print(f"  [{i}/{len(stocks)}] {ticker}...", end='\r')
        
        result = analyze_stock_simplified(ticker)
        if result:
            results.append(result)
        
        if i % 50 == 0:
            print(f"\n  ✓ Processed {i}/{len(stocks)} stocks...")
        
        time.sleep(0.5)
    
    print(f"\n✅ Completed at: {datetime.now().strftime('%H:%M:%S')}")
    
    df = pd.DataFrame(results)
    return df


def sector_scan(sector: str) -> pd.DataFrame:
    """Scan specific sector"""
    
    print(f"\n🔍 Scanning {sector.upper()} sector...")
    
    stocks = get_sector_stocks(sector)
    
    if not stocks:
        return pd.DataFrame()
    
    results = []
    
    for i, ticker in enumerate(stocks, 1):
        print(f"  [{i}/{len(stocks)}] {ticker}...", end='\r')
        result = analyze_stock_simplified(ticker)
        if result:
            results.append(result)
        time.sleep(0.5)
    
    print("\n✅ Sector scan completed!")
    
    return pd.DataFrame(results)


def custom_scan(tickers: List[str]) -> pd.DataFrame:
    """Scan custom list of tickers"""
    
    print(f"\n🔍 Custom scan of {len(tickers)} stocks...")
    
    results = []
    
    for i, ticker in enumerate(tickers, 1):
        # Add .JK if not present
        if not ticker.endswith('.JK'):
            ticker = f"{ticker}.JK"
        
        print(f"  [{i}/{len(tickers)}] {ticker}...", end='\r')
        result = analyze_stock_simplified(ticker)
        if result:
            results.append(result)
        time.sleep(0.5)
    
    print("\n✅ Custom scan completed!")
    
    return pd.DataFrame(results)


# ==============================================================================
# DEEP ANALYSIS MODE (Uses full Oracle analysis)
# ==============================================================================

def deep_market_scan(tickers: List[str]) -> List[Dict]:
    """Deep analysis using full Oracle engine"""
    
    print("\n" + "="*80)
    print("🔬 DEEP ANALYSIS MODE - Full Oracle Analysis")
    print("="*80)
    print(f"\n⚠️  This will take approximately {len(tickers) * 5} seconds")
    print(f"Analyzing {len(tickers)} stocks with full 3-pillar analysis...\n")
    
    # Try to import Oracle engine
    try:
        from main import OracleEngine
    except ImportError:
        print("❌ Error: main.py not found. Deep analysis requires main.py")
        print("Using simplified analysis instead...")
        df = custom_scan(tickers)
        return df.to_dict('records')
    
    results = []
    
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] Deep analysis: {ticker}")
        
        try:
            oracle = OracleEngine(ticker)
            analysis = oracle.analyze()
            
            results.append({
                'ticker': ticker,
                'signal': analysis['signal'],
                'score': analysis['final_score'],
                'confidence': analysis['confidence'],
                'fundamental': analysis['pillar_scores']['fundamental'],
                'technical': analysis['pillar_scores']['technical'],
                'sentiment': analysis['pillar_scores']['sentiment'],
                'holding_period': analysis['holding_period'],
                'price_target': analysis['price_targets']['long_term'],
                'current_price': analysis['current_price']
            })
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
        
        time.sleep(1)
    
    print("\n✅ Deep analysis completed!")
    return results


# ==============================================================================
# REPORT GENERATION - FIXED VERSION
# ==============================================================================

def generate_report(df: pd.DataFrame, scan_type: str = "market"):
    """Generate and save analysis report - FIXED to handle both scan types"""
    
    if df.empty:
        print("\n❌ No data to report")
        return
    
    # Create output directory
    output_dir = "market_analysis_results"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Print summary
    print("\n" + "="*80)
    print("📊 ANALYSIS SUMMARY")
    print("="*80)
    
    print(f"\nTotal Stocks Analyzed: {len(df)}")
    
    # Check if this is deep analysis or quick scan
    is_deep_analysis = 'confidence' in df.columns
    
    print(f"\nSignal Distribution:")
    if 'signal' in df.columns:
        signal_counts = df['signal'].value_counts()
        for signal, count in signal_counts.items():
            print(f"  {signal}: {count} ({count/len(df)*100:.1f}%)")
    
    # Only show sector distribution if it exists
    if 'sector' in df.columns:
        print(f"\nSector Distribution:")
        sector_counts = df['sector'].value_counts().head(10)
        for sector, count in sector_counts.items():
            print(f"  {sector}: {count}")
    
    # Top performers - only for quick scan
    if 'returns_1m' in df.columns:
        print(f"\n🚀 Top 10 Performers (1 Month):")
        top_10 = df.nlargest(10, 'returns_1m')[['ticker', 'returns_1m', 'signal']]
        if 'rsi' in df.columns:
            top_10 = df.nlargest(10, 'returns_1m')[['ticker', 'returns_1m', 'signal', 'rsi']]
        print(top_10.to_string(index=False))
        
        print(f"\n📉 Bottom 10 Performers (1 Month):")
        bottom_10 = df.nsmallest(10, 'returns_1m')[['ticker', 'returns_1m', 'signal']]
        if 'rsi' in df.columns:
            bottom_10 = df.nsmallest(10, 'returns_1m')[['ticker', 'returns_1m', 'signal', 'rsi']]
        print(bottom_10.to_string(index=False))
    
    # Buy recommendations - different handling for deep vs quick
    if 'signal' in df.columns:
        buy_signals = df[df['signal'] == 'BUY']
        if not buy_signals.empty:
            print(f"\n💰 BUY Signals ({len(buy_signals)} stocks):")
            
            if is_deep_analysis:
                # Deep analysis columns
                cols = ['ticker', 'score', 'confidence']
                if 'fundamental' in buy_signals.columns:
                    cols.append('fundamental')
                if 'technical' in buy_signals.columns:
                    cols.append('technical')
                buy_list = buy_signals.nlargest(15, 'score')[cols]
            else:
                # Quick scan columns
                cols = ['ticker', 'score']
                if 'returns_1m' in buy_signals.columns:
                    cols.append('returns_1m')
                if 'rsi' in buy_signals.columns:
                    cols.append('rsi')
                if 'sector' in buy_signals.columns:
                    cols.append('sector')
                buy_list = buy_signals.nlargest(15, 'score')[cols]
            
            print(buy_list.to_string(index=False))
    
    # Save to files
    csv_file = os.path.join(output_dir, f"idx_analysis_{timestamp}.csv")
    df.to_csv(csv_file, index=False)
    print(f"\n💾 Results saved to: {csv_file}")
    
    # Save to Excel if openpyxl available
    try:
        excel_file = os.path.join(output_dir, f"idx_analysis_{timestamp}.xlsx")
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"💾 Excel file saved to: {excel_file}")
    except:
        pass
    
    # Save summary JSON
    summary = {
        'scan_type': scan_type,
        'timestamp': timestamp,
        'total_stocks': len(df),
        'is_deep_analysis': is_deep_analysis,
        'signal_distribution': df['signal'].value_counts().to_dict() if 'signal' in df.columns else {},
        'buy_signals': df[df['signal'] == 'BUY']['ticker'].tolist() if 'signal' in df.columns else []
    }
    
    if 'returns_1m' in df.columns:
        summary['top_10_tickers'] = df.nlargest(10, 'returns_1m')['ticker'].tolist()
    
    json_file = os.path.join(output_dir, f"summary_{timestamp}.json")
    with open(json_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"💾 Summary saved to: {json_file}")
    print("\n" + "="*80)


# ==============================================================================
# MAIN MENU
# ==============================================================================

def main():
    """Main interactive menu"""
    
    print("\n" + "="*80)
    print("🔮 PROJECT ORACLE - INDONESIAN MARKET SCANNER")
    print("="*80)
    print("\nScan Modes:")
    print("1. Quick Scan (~100 major stocks, 3-5 minutes)")
    print("2. Full Market Scan (~700 stocks, 20-30 minutes)")
    print("3. Deep Analysis (Full Oracle, very slow)")
    print("4. Sector Analysis")
    print("5. Custom Stock List")
    print("6. Exit")
    
    choice = input("\nSelect mode (1-6): ").strip()
    
    if choice == '1':
        df = quick_scan()
        generate_report(df, "quick_scan")
        
    elif choice == '2':
        confirm = input("\n⚠️  This will take 20-30 minutes. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            df = full_market_scan()
            generate_report(df, "full_scan")
        
    elif choice == '3':
        tickers_input = input("\nEnter tickers (comma-separated, e.g., BBCA.JK,TLKM.JK): ")
        tickers = [t.strip() for t in tickers_input.split(',')]
        results = deep_market_scan(tickers)
        df = pd.DataFrame(results)
        generate_report(df, "deep_analysis")
        
    elif choice == '4':
        print("\nAvailable sectors:")
        for sector in SECTOR_MAPPING.keys():
            print(f"  • {sector.title()}")
        
        sector_name = input("\nEnter sector name: ").strip()
        df = sector_scan(sector_name)
        generate_report(df, f"sector_{sector_name}")
        
    elif choice == '5':
        print("\nEnter tickers separated by commas (e.g., BBCA.JK,TLKM.JK,ASII.JK):")
        tickers_input = input("Tickers: ").strip()
        tickers = [t.strip() for t in tickers_input.split(',')]
        df = custom_scan(tickers)
        generate_report(df, "custom_scan")
        
    elif choice == '6':
        print("\n👋 Goodbye!")
        return
    
    else:
        print("\n❌ Invalid choice.")
        return
    
    # Ask to continue
    another = input("\n\nRun another scan? (yes/no): ")
    if another.lower() == 'yes':
        main()


# ==============================================================================
# COMMAND LINE INTERFACE
# ==============================================================================

if __name__ == "__main__":
    # Run interactive menu
    main()