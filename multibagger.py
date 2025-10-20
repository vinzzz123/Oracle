"""
PROJECT ORACLE - MULTIBAGGER HUNTER MODULE
===========================================
Advanced multibagger detection system combining Peter Lynch methodology
with Indonesian market catalysts and corporate action signals.

Author: Project Oracle Team
Version: 1.0
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class MultibaggerHunter:
    """
    Specialized scanner for identifying potential multibagger stocks
    (3x - 10x+ return opportunities over 1-3 years)
    """
    
    def __init__(self, market: str = "IDX"):
        self.market = market
        self.min_score = 70  # Minimum score for consideration
        self.indonesian_themes = {
            'Mining': 2.0,
            'Energy': 1.5,
            'Technology': 2.0,
            'Consumer Cyclical': 1.5,
            'Financial Services': 1.0,
            'Industrials': 1.5,
            'Basic Materials': 1.5,
        }
    
    def scan_market(self, tickers: List[str]) -> pd.DataFrame:
        """
        Main scanning function - finds multibagger candidates
        
        Args:
            tickers: List of stock tickers to scan
            
        Returns:
            DataFrame with multibagger candidates ranked by score
        """
        print("\n" + "="*80)
        print("🎯 MULTIBAGGER HUNTER - INITIATED")
        print("="*80)
        print(f"Scanning {len(tickers)} stocks for multibagger potential...")
        
        results = []
        
        for i, ticker in enumerate(tickers, 1):
            if i % 10 == 0:
                print(f"Progress: {i}/{len(tickers)} stocks analyzed...")
            
            try:
                analysis = self.analyze_multibagger_potential(ticker)
                if analysis and analysis['multibagger_score'] >= self.min_score:
                    results.append(analysis)
            except Exception as e:
                continue
        
        if not results:
            print("\n❌ No multibagger candidates found matching criteria")
            return pd.DataFrame()
        
        # Convert to DataFrame and sort
        df = pd.DataFrame(results)
        df = df.sort_values('multibagger_score', ascending=False)
        
        print(f"\n✅ Found {len(df)} potential multibagger candidates!")
        return df
    
    def analyze_multibagger_potential(self, ticker: str) -> Optional[Dict]:
        """
        Deep analysis of a single stock for multibagger potential
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")
            
            if hist.empty or len(hist) < 50:
                return None
            
            # Calculate all components
            size_score = self._calculate_size_score(info)
            growth_score = self._calculate_growth_score(info)
            valuation_score = self._calculate_valuation_score(info)
            quality_score = self._calculate_quality_score(info)
            catalyst_score = self._calculate_catalyst_score(ticker, stock, info, hist)
            momentum_score = self._calculate_momentum_score(hist)
            
            # Weighted final score
            multibagger_score = (
                size_score * 0.20 +
                growth_score * 0.25 +
                valuation_score * 0.15 +
                quality_score * 0.15 +
                catalyst_score * 0.15 +
                momentum_score * 0.10
            )
            
            # Detect specific catalysts
            catalysts = self._detect_catalysts(ticker, stock, info, hist)
            
            # Risk assessment
            risk_level = self._assess_risk(info, hist)
            
            # Expected return range
            return_potential = self._estimate_return_potential(
                multibagger_score, len(catalysts)
            )
            
            return {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'multibagger_score': round(multibagger_score, 2),
                'size_score': round(size_score, 2),
                'growth_score': round(growth_score, 2),
                'valuation_score': round(valuation_score, 2),
                'quality_score': round(quality_score, 2),
                'catalyst_score': round(catalyst_score, 2),
                'momentum_score': round(momentum_score, 2),
                'catalysts': catalysts,
                'num_catalysts': len(catalysts),
                'risk_level': risk_level,
                'return_potential': return_potential,
                'market_cap': info.get('marketCap', 0),
                'current_price': hist['Close'].iloc[-1],
                'pe_ratio': info.get('trailingPE', None),
                'peg_ratio': info.get('pegRatio', None),
                'revenue_growth': info.get('revenueGrowth', None),
                'profit_margin': info.get('profitMargins', None),
            }
            
        except Exception as e:
            return None
    
    def _calculate_size_score(self, info: Dict) -> float:
        """
        Peter Lynch: Small companies have big moves
        Sweet spot: 500M - 5B market cap
        """
        mcap = info.get('marketCap', 0)
        
        if mcap == 0:
            return 0
        
        # Convert to billions for easier comparison
        mcap_b = mcap / 1_000_000_000
        
        if mcap_b < 0.5:  # < 500M - too small/risky
            return 40
        elif mcap_b < 1:  # 500M - 1B - excellent
            return 100
        elif mcap_b < 3:  # 1B - 3B - very good
            return 85
        elif mcap_b < 5:  # 3B - 5B - good
            return 70
        elif mcap_b < 10:  # 5B - 10B - moderate
            return 50
        else:  # > 10B - low multibagger potential
            return 30
    
    def _calculate_growth_score(self, info: Dict) -> float:
        """
        Lynch's Fast Growers: 20-25% growth annually
        Higher growth = higher score, but cap at 50% to avoid unsustainable
        """
        score = 0
        
        # Revenue growth
        rev_growth = info.get('revenueGrowth', 0)
        if rev_growth:
            if rev_growth > 0.50:  # >50% - excellent but risky
                score += 35
            elif rev_growth > 0.30:  # >30% - excellent
                score += 40
            elif rev_growth > 0.20:  # >20% - very good
                score += 35
            elif rev_growth > 0.10:  # >10% - moderate
                score += 20
            else:
                score += 5
        
        # Earnings growth
        earnings_growth = info.get('earningsGrowth', 0)
        if earnings_growth:
            if earnings_growth > 0.40:  # >40% - excellent
                score += 40
            elif earnings_growth > 0.25:  # >25% - very good
                score += 35
            elif earnings_growth > 0.15:  # >15% - good
                score += 25
            else:
                score += 10
        
        # Quarterly growth (momentum)
        q_rev_growth = info.get('revenueQuarterlyGrowth', 0)
        if q_rev_growth and q_rev_growth > 0.20:
            score += 20
        
        return min(score, 100)
    
    def _calculate_valuation_score(self, info: Dict) -> float:
        """
        PEG Ratio < 2 is ideal (Lynch's key metric)
        But also check absolute PE to avoid value traps
        """
        score = 0
        
        # PEG Ratio (Price/Earnings to Growth)
        peg = info.get('pegRatio', None)
        if peg:
            if 0 < peg < 0.5:  # Deep value
                score += 50
            elif peg < 1:  # Excellent value
                score += 45
            elif peg < 1.5:  # Good value
                score += 35
            elif peg < 2:  # Fair value
                score += 25
            else:  # Expensive
                score += 10
        else:
            score += 20  # Neutral if no PEG
        
        # PE Ratio check
        pe = info.get('trailingPE', None)
        if pe:
            if 5 < pe < 15:  # Sweet spot
                score += 30
            elif 15 <= pe < 25:  # Reasonable
                score += 25
            elif 25 <= pe < 40:  # Growth premium
                score += 15
            else:
                score += 5
        
        # Price to Book
        pb = info.get('priceToBook', None)
        if pb and 0 < pb < 3:
            score += 20
        
        return min(score, 100)
    
    def _calculate_quality_score(self, info: Dict) -> float:
        """
        Financial health and profitability metrics
        """
        score = 0
        
        # Profitability
        profit_margin = info.get('profitMargins', 0)
        if profit_margin:
            if profit_margin > 0.20:  # >20% - excellent
                score += 25
            elif profit_margin > 0.10:  # >10% - good
                score += 20
            elif profit_margin > 0.05:  # >5% - acceptable
                score += 15
            else:
                score += 5
        
        # Return on Equity
        roe = info.get('returnOnEquity', 0)
        if roe:
            if roe > 0.25:  # >25% - excellent
                score += 25
            elif roe > 0.15:  # >15% - good
                score += 20
            elif roe > 0.10:  # >10% - acceptable
                score += 15
            else:
                score += 5
        
        # Debt levels (Lynch avoided debt bombs)
        debt_to_equity = info.get('debtToEquity', 0)
        if debt_to_equity:
            if debt_to_equity < 30:  # <0.3 - very safe
                score += 25
            elif debt_to_equity < 50:  # <0.5 - safe
                score += 20
            elif debt_to_equity < 100:  # <1.0 - moderate
                score += 15
            else:  # >1.0 - risky
                score += 5
        else:
            score += 20  # No debt reported = possibly debt-free
        
        # Current Ratio
        current_ratio = info.get('currentRatio', 0)
        if current_ratio:
            if current_ratio > 2:
                score += 15
            elif current_ratio > 1.5:
                score += 12
            elif current_ratio > 1:
                score += 8
        
        # Operating Cash Flow
        if info.get('operatingCashflow', 0) > 0:
            score += 10
        
        return min(score, 100)
    
    def _calculate_catalyst_score(self, ticker: str, stock, info: Dict, 
                                  hist: pd.DataFrame) -> float:
        """
        Detect potential catalysts that could drive multibagger returns
        """
        score = 0
        
        # Volume anomaly (potential corporate action signal)
        avg_volume = hist['Volume'].mean()
        recent_volume = hist['Volume'].tail(20).mean()
        if avg_volume > 0:
            volume_ratio = recent_volume / avg_volume
            if volume_ratio > 3:  # 3x normal volume
                score += 30
            elif volume_ratio > 2:
                score += 20
            elif volume_ratio > 1.5:
                score += 10
        
        # Sector momentum (hot Indonesian sectors)
        sector = info.get('sector', '')
        sector_boost = self.indonesian_themes.get(sector, 0)
        score += sector_boost * 15
        
        # Insider ownership (skin in the game)
        insider_pct = info.get('heldPercentInsiders', 0)
        if insider_pct:
            if insider_pct > 0.30:  # >30%
                score += 20
            elif insider_pct > 0.20:
                score += 15
            elif insider_pct > 0.10:
                score += 10
        
        # Low institutional ownership (room for discovery)
        inst_pct = info.get('heldPercentInstitutions', 0)
        if inst_pct:
            if inst_pct < 0.30:  # <30% - underowned
                score += 15
            elif inst_pct < 0.50:
                score += 10
        
        # Explosive recent growth
        rev_growth = info.get('revenueGrowth', 0)
        if rev_growth and rev_growth > 0.50:  # >50% growth
            score += 20
        
        return min(score, 100)
    
    def _calculate_momentum_score(self, hist: pd.DataFrame) -> float:
        """
        Technical momentum indicators
        """
        score = 0
        
        if len(hist) < 50:
            return 0
        
        current_price = hist['Close'].iloc[-1]
        
        # 6-month momentum
        if len(hist) >= 126:
            price_6m_ago = hist['Close'].iloc[-126]
            momentum_6m = (current_price / price_6m_ago - 1) * 100
            
            if momentum_6m > 50:
                score += 30
            elif momentum_6m > 25:
                score += 25
            elif momentum_6m > 10:
                score += 20
            elif momentum_6m > 0:
                score += 10
        
        # 3-month momentum
        if len(hist) >= 63:
            price_3m_ago = hist['Close'].iloc[-63]
            momentum_3m = (current_price / price_3m_ago - 1) * 100
            
            if momentum_3m > 30:
                score += 25
            elif momentum_3m > 15:
                score += 20
            elif momentum_3m > 5:
                score += 15
        
        # Relative Strength Index
        try:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            if 40 <= current_rsi <= 70:  # Sweet spot - not overbought
                score += 20
            elif 30 <= current_rsi < 40:  # Oversold - potential bounce
                score += 15
        except:
            pass
        
        # Price above moving averages
        ma50 = hist['Close'].rolling(50).mean().iloc[-1]
        ma200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None
        
        if current_price > ma50:
            score += 15
        if ma200 and current_price > ma200:
            score += 10
        
        return min(score, 100)
    
    def _detect_catalysts(self, ticker: str, stock, info: Dict, 
                         hist: pd.DataFrame) -> List[str]:
        """
        Identify specific catalysts present
        """
        catalysts = []
        
        # Volume anomaly
        avg_volume = hist['Volume'].mean()
        recent_volume = hist['Volume'].tail(20).mean()
        if avg_volume > 0 and (recent_volume / avg_volume) > 2.5:
            catalysts.append('UNUSUAL_VOLUME')
        
        # Explosive growth
        rev_growth = info.get('revenueGrowth', 0)
        if rev_growth and rev_growth > 0.40:
            catalysts.append('EXPLOSIVE_GROWTH')
        
        # Hot sector
        sector = info.get('sector', '')
        if sector in self.indonesian_themes and self.indonesian_themes[sector] >= 1.5:
            catalysts.append('HOT_SECTOR')
        
        # Strong momentum
        if len(hist) >= 126:
            current_price = hist['Close'].iloc[-1]
            price_6m_ago = hist['Close'].iloc[-126]
            momentum_6m = (current_price / price_6m_ago - 1) * 100
            if momentum_6m > 30:
                catalysts.append('STRONG_MOMENTUM')
        
        # Undervalued growth (PEG < 1)
        peg = info.get('pegRatio', None)
        if peg and 0 < peg < 1:
            catalysts.append('UNDERVALUED_GROWTH')
        
        # High insider ownership
        insider_pct = info.get('heldPercentInsiders', 0)
        if insider_pct and insider_pct > 0.25:
            catalysts.append('HIGH_INSIDER_OWNERSHIP')
        
        # Small cap with high growth
        mcap = info.get('marketCap', 0)
        if mcap < 2_000_000_000 and rev_growth and rev_growth > 0.25:
            catalysts.append('SMALL_CAP_GROWTH')
        
        # Recent breakout
        if len(hist) >= 50:
            ma50 = hist['Close'].rolling(50).mean().iloc[-1]
            current_price = hist['Close'].iloc[-1]
            if current_price > ma50 * 1.05:  # 5% above MA50
                catalysts.append('TECHNICAL_BREAKOUT')
        
        return catalysts
    
    def _assess_risk(self, info: Dict, hist: pd.DataFrame) -> str:
        """
        Assess overall risk level
        """
        risk_points = 0
        
        # Market cap risk
        mcap = info.get('marketCap', 0)
        if mcap < 500_000_000:
            risk_points += 3
        elif mcap < 2_000_000_000:
            risk_points += 2
        elif mcap < 5_000_000_000:
            risk_points += 1
        
        # Debt risk
        debt_to_equity = info.get('debtToEquity', 0)
        if debt_to_equity and debt_to_equity > 100:
            risk_points += 2
        elif debt_to_equity and debt_to_equity > 50:
            risk_points += 1
        
        # Profitability risk
        profit_margin = info.get('profitMargins', 0)
        if profit_margin and profit_margin < 0:
            risk_points += 3
        elif profit_margin and profit_margin < 0.05:
            risk_points += 2
        
        # Volatility risk
        if len(hist) >= 30:
            returns = hist['Close'].pct_change()
            volatility = returns.std() * np.sqrt(252)  # Annualized
            if volatility > 0.60:  # >60% annual volatility
                risk_points += 2
            elif volatility > 0.40:
                risk_points += 1
        
        if risk_points >= 6:
            return "VERY_HIGH"
        elif risk_points >= 4:
            return "HIGH"
        elif risk_points >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_return_potential(self, score: float, num_catalysts: int) -> str:
        """
        Estimate potential return range based on score and catalysts
        """
        if score >= 85 and num_catalysts >= 4:
            return "500-1000%+ (10-bagger potential)"
        elif score >= 80 and num_catalysts >= 3:
            return "300-500% (4-6 bagger)"
        elif score >= 75 and num_catalysts >= 2:
            return "200-300% (3-4 bagger)"
        elif score >= 70:
            return "100-200% (2-3 bagger)"
        else:
            return "50-100% (modest multibagger)"
    
    def generate_report(self, df: pd.DataFrame, output_file: str = None):
        """
        Generate detailed multibagger report
        """
        if df.empty:
            print("\n❌ No data to report")
            return
        
        print("\n" + "="*80)
        print("📊 MULTIBAGGER HUNTER - FINAL REPORT")
        print("="*80)
        
        print(f"\nTotal Candidates Found: {len(df)}")
        print(f"Average Multibagger Score: {df['multibagger_score'].mean():.2f}")
        
        # Top 10
        print("\n🏆 TOP 10 MULTIBAGGER CANDIDATES:")
        print("-" * 80)
        
        top_10 = df.head(10)
        for i, row in top_10.iterrows():
            print(f"\n#{i+1}. {row['ticker']} - {row['name']}")
            print(f"   Score: {row['multibagger_score']:.1f}/100 | Sector: {row['sector']}")
            print(f"   Market Cap: ${row['market_cap']:,.0f}")
            print(f"   Catalysts ({row['num_catalysts']}): {', '.join(row['catalysts'])}")
            print(f"   Risk Level: {row['risk_level']}")
            print(f"   Return Potential: {row['return_potential']}")
            print(f"   Current Price: ${row['current_price']:.2f}")
            if row['pe_ratio']:
                print(f"   P/E: {row['pe_ratio']:.2f}", end="")
            if row['peg_ratio']:
                print(f" | PEG: {row['peg_ratio']:.2f}", end="")
            print()
        
        # Sector distribution
        print("\n📈 SECTOR DISTRIBUTION:")
        sector_counts = df['sector'].value_counts()
        for sector, count in sector_counts.items():
            print(f"   {sector}: {count}")
        
        # Risk distribution
        print("\n⚠️  RISK DISTRIBUTION:")
        risk_counts = df['risk_level'].value_counts()
        for risk, count in risk_counts.items():
            print(f"   {risk}: {count}")
        
        # Most common catalysts
        print("\n🔥 MOST COMMON CATALYSTS:")
        all_catalysts = []
        for catalysts in df['catalysts']:
            all_catalysts.extend(catalysts)
        catalyst_counts = pd.Series(all_catalysts).value_counts()
        for catalyst, count in catalyst_counts.head(10).items():
            print(f"   {catalyst}: {count}")
        
        # Save to CSV
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"\n💾 Report saved to: {output_file}")
        
        print("\n" + "="*80)
        print("⚠️  DISCLAIMER: High-risk, high-reward plays. Do your own research!")
        print("    Position size: Max 5% per stock | Diversify: 10-20 picks")
        print("    Time horizon: 1-3 years minimum | Use stop losses!")
        print("="*80)


def quick_multibagger_scan(tickers: List[str], top_n: int = 50) -> List[str]:
    """
    Quick pre-filter to find top candidates before deep analysis
    Returns list of tickers for deep dive
    """
    print("\n🔍 Quick Multibagger Pre-Filter...")
    candidates = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Quick filters
            mcap = info.get('marketCap', 0)
            rev_growth = info.get('revenueGrowth', 0)
            
            # Must be small-mid cap
            if not (500_000_000 <= mcap <= 10_000_000_000):
                continue
            
            # Must be growing
            if not rev_growth or rev_growth < 0.15:
                continue
            
            # Must be profitable
            profit_margin = info.get('profitMargins', 0)
            if not profit_margin or profit_margin < 0:
                continue
            
            score = 0
            if mcap < 2_000_000_000:
                score += 3
            if rev_growth > 0.30:
                score += 3
            if profit_margin > 0.10:
                score += 2
            
            candidates.append((ticker, score))
            
        except:
            continue
    
    # Sort and return top N
    candidates.sort(key=lambda x: x[1], reverse=True)
    top_tickers = [t[0] for t in candidates[:top_n]]
    
    print(f"✅ Pre-filtered to top {len(top_tickers)} candidates for deep analysis")
    return top_tickers


# Example usage
if __name__ == "__main__":
    print("Multibagger Hunter Module Loaded")
    print("Import this module into your main.py")