"""
PROJECT ORACLE - MAIN INTERFACE
================================
Updated with Multibagger Hunter Integration

Usage:
    python main.py

Menu Options:
    1. Single Stock Analysis (Deep)
    2. Quick Market Scan
    3. Custom Stock List Analysis
    4. 🆕 MULTIBAGGER HUNTER - Full Market
    5. 🆕 MULTIBAGGER HUNTER - Sector Focus
    6. 🆕 MULTIBAGGER HUNTER - Quick Pre-Screen
"""

import os
import sys
import time
import pandas as pd
from datetime import datetime
from typing import List

# Import existing modules
# from oracle_engine import OracleEngine  # Your existing deep analysis
from multibagger import MultibaggerHunter, quick_multibagger_scan

# If you don't have oracle_engine yet, comment it out and use simplified version


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Display Project Oracle banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║            🔮 PROJECT ORACLE - STOCK ANALYSIS 🔮             ║
    ║                                                               ║
    ║              "Your Edge in Finding Multibaggers"             ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def get_idx_tickers() -> List[str]:
    """
    Get list of Indonesian stock tickers
    
    NOTE: Replace this with your actual IDX ticker list
    For now, using some example tickers
    """
    # Example tickers - replace with full IDX list
    idx_tickers = [
        "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK",  # Banking
        "TLKM.JK", "EXCL.JK",  # Telecom
        "ASII.JK", "UNTR.JK",  # Automotive/Heavy Equipment
        "ICBP.JK", "INDF.JK",  # Consumer
        "ADRO.JK", "PTBA.JK", "ITMG.JK",  # Coal Mining
        "ANTM.JK", "MDKA.JK",  # Metals & Mining
        "PGAS.JK",  # Energy
        "WSKT.JK", "WIKA.JK", "PTPP.JK",  # Construction
        "CPIN.JK", "JPFA.JK",  # Poultry/Agriculture
    ]
    
    # TODO: Load full IDX ticker list from file or API
    # with open('idx_tickers.txt', 'r') as f:
    #     idx_tickers = [line.strip() for line in f.readlines()]
    
    return idx_tickers


def get_sector_tickers(sector: str) -> List[str]:
    """Get tickers for specific sector"""
    
    sectors = {
        'Banking': ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK"],
        'Mining': ["ADRO.JK", "PTBA.JK", "ITMG.JK", "ANTM.JK", "MDKA.JK", "INCO.JK"],
        'Technology': ["GOTO.JK", "BUKA.JK", "WIFI.JK"],
        'Consumer': ["ICBP.JK", "INDF.JK", "MYOR.JK", "ULTJ.JK"],
        'Construction': ["WSKT.JK", "WIKA.JK", "PTPP.JK", "ADHI.JK"],
    }
    
    return sectors.get(sector, [])


def single_stock_analysis():
    """Analyze a single stock in depth"""
    print("\n" + "="*70)
    print("📊 SINGLE STOCK DEEP ANALYSIS")
    print("="*70)
    
    ticker = input("\nEnter stock ticker (e.g., BBCA.JK): ").strip().upper()
    
    if not ticker:
        print("❌ No ticker provided")
        return
    
    # Add .JK if not present for Indonesian stocks
    if not ticker.endswith('.JK'):
        ticker += '.JK'
    
    print(f"\n🔍 Analyzing {ticker}...")
    
    # Option 1: Use full OracleEngine if available
    # try:
    #     oracle = OracleEngine(ticker)
    #     result = oracle.analyze()
    #     oracle.print_report(result)
    # except Exception as e:
    #     print(f"❌ Error: {e}")
    
    # Option 2: Use MultibaggerHunter for analysis
    hunter = MultibaggerHunter()
    result = hunter.analyze_multibagger_potential(ticker)
    
    if result:
        print("\n" + "="*70)
        print(f"🎯 MULTIBAGGER ANALYSIS: {result['ticker']}")
        print("="*70)
        print(f"\nCompany: {result['name']}")
        print(f"Sector: {result['sector']}")
        print(f"Current Price: ${result['current_price']:.2f}")
        print(f"Market Cap: ${result['market_cap']:,.0f}")
        
        print(f"\n📊 MULTIBAGGER SCORE: {result['multibagger_score']:.1f}/100")
        print(f"   - Size Score: {result['size_score']:.1f}")
        print(f"   - Growth Score: {result['growth_score']:.1f}")
        print(f"   - Valuation Score: {result['valuation_score']:.1f}")
        print(f"   - Quality Score: {result['quality_score']:.1f}")
        print(f"   - Catalyst Score: {result['catalyst_score']:.1f}")
        print(f"   - Momentum Score: {result['momentum_score']:.1f}")
        
        print(f"\n🔥 CATALYSTS ({result['num_catalysts']}):")
        for catalyst in result['catalysts']:
            print(f"   ✓ {catalyst}")
        
        print(f"\n⚠️  RISK LEVEL: {result['risk_level']}")
        print(f"🎯 RETURN POTENTIAL: {result['return_potential']}")
        
        if result['pe_ratio']:
            print(f"\n📈 P/E Ratio: {result['pe_ratio']:.2f}")
        if result['peg_ratio']:
            print(f"   PEG Ratio: {result['peg_ratio']:.2f}")
        if result['revenue_growth']:
            print(f"   Revenue Growth: {result['revenue_growth']*100:.1f}%")
        if result['profit_margin']:
            print(f"   Profit Margin: {result['profit_margin']*100:.1f}%")
    else:
        print("❌ Could not analyze this stock")


def multibagger_full_market_scan():
    """Full market multibagger scan"""
    print("\n" + "="*70)
    print("🎯 MULTIBAGGER HUNTER - FULL MARKET SCAN")
    print("="*70)
    
    print("\n⚠️  WARNING: This will analyze ALL stocks in the market")
    print("   Expected time: 30-60 minutes for full IDX")
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Scan cancelled")
        return
    
    # Get all tickers
    tickers = get_idx_tickers()
    print(f"\n📋 Found {len(tickers)} tickers to analyze")
    
    # Option: Two-stage approach (RECOMMENDED)
    use_prefilter = input("\nUse quick pre-filter first? (recommended, yes/no): ").strip().lower()
    
    if use_prefilter == 'yes':
        print("\n🔍 Stage 1: Quick pre-filtering...")
        tickers = quick_multibagger_scan(tickers, top_n=100)
        print(f"\n✅ Filtered to {len(tickers)} candidates for deep analysis")
    
    # Deep analysis
    print("\n🔬 Stage 2: Deep multibagger analysis...")
    hunter = MultibaggerHunter()
    results = hunter.scan_market(tickers)
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"multibagger_scan_{timestamp}.csv"
    hunter.generate_report(results, output_file)
    
    print(f"\n✅ Analysis complete! Check: {output_file}")


def multibagger_sector_scan():
    """Scan specific sector for multibaggers"""
    print("\n" + "="*70)
    print("🎯 MULTIBAGGER HUNTER - SECTOR FOCUS")
    print("="*70)
    
    print("\nAvailable Sectors:")
    print("1. Banking")
    print("2. Mining")
    print("3. Technology")
    print("4. Consumer")
    print("5. Construction")
    
    choice = input("\nSelect sector (1-5): ").strip()
    
    sector_map = {
        '1': 'Banking',
        '2': 'Mining',
        '3': 'Technology',
        '4': 'Consumer',
        '5': 'Construction',
    }
    
    sector = sector_map.get(choice)
    
    if not sector:
        print("❌ Invalid selection")
        return
    
    tickers = get_sector_tickers(sector)
    
    if not tickers:
        print(f"❌ No tickers found for {sector}")
        return
    
    print(f"\n🔍 Analyzing {len(tickers)} stocks in {sector} sector...")
    
    hunter = MultibaggerHunter()
    results = hunter.scan_market(tickers)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"multibagger_{sector.lower()}_{timestamp}.csv"
    hunter.generate_report(results, output_file)


def multibagger_quick_screen():
    """Quick multibagger pre-screen (fast overview)"""
    print("\n" + "="*70)
    print("⚡ MULTIBAGGER QUICK PRE-SCREEN")
    print("="*70)
    
    tickers = get_idx_tickers()
    print(f"\n🔍 Quick screening {len(tickers)} stocks...")
    
    top_tickers = quick_multibagger_scan(tickers, top_n=50)
    
    print(f"\n✅ Top {len(top_tickers)} Candidates:")
    for i, ticker in enumerate(top_tickers, 1):
        print(f"   {i}. {ticker}")
    
    print("\n💡 TIP: Use 'Custom Stock List Analysis' to deep-dive these tickers")
    
    # Save list
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quick_screen_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write('\n'.join(top_tickers))
    
    print(f"\n💾 Saved to: {filename}")


def custom_list_analysis():
    """Analyze custom list of stocks"""
    print("\n" + "="*70)
    print("📝 CUSTOM STOCK LIST ANALYSIS")
    print("="*70)
    
    print("\nEnter stock tickers (comma-separated)")
    print("Example: BBCA.JK,TLKM.JK,ASII.JK")
    
    ticker_input = input("\nTickers: ").strip()
    
    if not ticker_input:
        print("❌ No tickers provided")
        return
    
    # Parse tickers
    tickers = [t.strip().upper() for t in ticker_input.split(',')]
    
    # Add .JK if missing
    tickers = [t if t.endswith('.JK') else t + '.JK' for t in tickers]
    
    print(f"\n🔍 Analyzing {len(tickers)} stocks...")
    
    hunter = MultibaggerHunter()
    results = hunter.scan_market(tickers)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"custom_analysis_{timestamp}.csv"
    hunter.generate_report(results, output_file)


def display_menu():
    """Display main menu"""
    print("\n" + "="*70)
    print("MAIN MENU")
    print("="*70)
    print("\n📊 ANALYSIS OPTIONS:")
    print("   1. Single Stock Analysis (Deep)")
    print("   2. Custom Stock List Analysis")
    
    print("\n🎯 MULTIBAGGER HUNTER:")
    print("   3. Full Market Scan (All Stocks)")
    print("   4. Sector-Focused Scan")
    print("   5. Quick Pre-Screen (Fast Overview)")
    
    print("\n⚙️  OTHER:")
    print("   6. Settings & Info")
    print("   0. Exit")
    
    print("\n" + "="*70)


def show_info():
    """Show information about the system"""
    print("\n" + "="*70)
    print("ℹ️  PROJECT ORACLE - INFORMATION")
    print("="*70)
    
    print("\n🎯 WHAT IS MULTIBAGGER HUNTER?")
    print("   A specialized module that scans for stocks with 3x-10x+ potential")
    print("   Based on Peter Lynch's methodology + Indonesian market catalysts")
    
    print("\n🔍 WHAT IT ANALYZES:")
    print("   ✓ Company Size (small = higher potential)")
    print("   ✓ Growth Rate (20-50% revenue/earnings growth)")
    print("   ✓ Valuation (PEG ratio < 2)")
    print("   ✓ Quality (profitability, low debt)")
    print("   ✓ Catalysts (volume spikes, sector themes, insider buying)")
    print("   ✓ Momentum (technical breakouts)")
    
    print("\n⚠️  RISK WARNINGS:")
    print("   • Multibaggers are HIGH RISK, HIGH REWARD")
    print("   • Position size: MAX 5% per stock")
    print("   • Diversify: Hold 10-20 candidates")
    print("   • Time horizon: 1-3 years MINIMUM")
    print("   • Use stop losses (-30% to -50%)")
    print("   • Do your own research - this is a tool, not advice!")
    
    print("\n📚 STRATEGY:")
    print("   'You only need 2-3 ten-baggers out of 20 picks")
    print("    to make your portfolio soar' - Peter Lynch")
    
    print("\n📁 FILES GENERATED:")
    print("   • CSV reports with full analysis")
    print("   • Ranked by multibagger score")
    print("   • Includes catalysts and risk assessment")


def main():
    """Main program loop"""
    while True:
        clear_screen()
        print_banner()
        display_menu()
        
        choice = input("\nSelect option (0-6): ").strip()
        
        if choice == '0':
            print("\n👋 Thank you for using Project Oracle!")
            print("   Happy investing! 🚀\n")
            break
        
        elif choice == '1':
            single_stock_analysis()
        
        elif choice == '2':
            custom_list_analysis()
        
        elif choice == '3':
            multibagger_full_market_scan()
        
        elif choice == '4':
            multibagger_sector_scan()
        
        elif choice == '5':
            multibagger_quick_screen()
        
        elif choice == '6':
            show_info()
        
        else:
            print("\n❌ Invalid option. Please select 0-6")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue.")
        sys.exit(1)