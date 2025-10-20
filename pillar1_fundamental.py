"""
PILLAR 1: FUNDAMENTAL ANALYSIS
Analyzes company fundamentals from financial statements

File: pillar1_fundamental.py
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime

class FundamentalAnalyzer:
    """Analyzes fundamental metrics from financial statements"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        
    def analyze(self) -> Dict:
        """Perform complete fundamental analysis"""
        
        # Get all data
        info = self.stock.info
        financials = self.stock.financials
        balance_sheet = self.stock.balance_sheet
        cash_flow = self.stock.cashflow
        
        # Calculate individual metrics
        valuation_score = self._analyze_valuation(info)
        profitability_score = self._analyze_profitability(info, financials)
        financial_health_score = self._analyze_financial_health(info, balance_sheet)
        growth_score = self._analyze_growth(info, financials)
        dividend_score = self._analyze_dividends(info)
        
        # Calculate weighted overall score
        weights = {
            'valuation': 0.25,
            'profitability': 0.25,
            'financial_health': 0.20,
            'growth': 0.20,
            'dividends': 0.10
        }
        
        total_score = (
            valuation_score * weights['valuation'] +
            profitability_score * weights['profitability'] +
            financial_health_score * weights['financial_health'] +
            growth_score * weights['growth'] +
            dividend_score * weights['dividends']
        )
        
        # Determine rating
        if total_score >= 80:
            rating = "STRONG BUY"
        elif total_score >= 65:
            rating = "BUY"
        elif total_score >= 45:
            rating = "HOLD"
        elif total_score >= 30:
            rating = "SELL"
        else:
            rating = "STRONG SELL"
        
        return {
            'score': total_score,
            'rating': rating,
            'components': {
                'valuation': valuation_score,
                'profitability': profitability_score,
                'financial_health': financial_health_score,
                'growth': growth_score,
                'dividends': dividend_score
            },
            'metrics': self._extract_key_metrics(info)
        }
    
    def _analyze_valuation(self, info: Dict) -> float:
        """Analyze valuation metrics (P/E, P/B, PEG, etc.)"""
        score = 50  # Neutral baseline
        
        try:
            # P/E Ratio analysis
            pe = info.get('trailingPE', None)
            if pe:
                if pe < 15:
                    score += 15
                elif pe < 25:
                    score += 10
                elif pe < 35:
                    score += 5
                elif pe > 50:
                    score -= 15
                elif pe > 40:
                    score -= 10
            
            # P/B Ratio analysis
            pb = info.get('priceToBook', None)
            if pb:
                if pb < 1:
                    score += 15
                elif pb < 3:
                    score += 10
                elif pb < 5:
                    score += 5
                elif pb > 10:
                    score -= 10
            
            # PEG Ratio analysis
            peg = info.get('pegRatio', None)
            if peg:
                if peg < 1:
                    score += 15
                elif peg < 1.5:
                    score += 10
                elif peg < 2:
                    score += 5
                elif peg > 3:
                    score -= 10
            
            # Price to Sales
            ps = info.get('priceToSalesTrailing12Months', None)
            if ps:
                if ps < 2:
                    score += 10
                elif ps < 5:
                    score += 5
                elif ps > 10:
                    score -= 10
                    
        except Exception as e:
            print(f"Valuation analysis error: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_profitability(self, info: Dict, financials: pd.DataFrame) -> float:
        """Analyze profitability metrics (ROE, ROA, margins, etc.)"""
        score = 50
        
        try:
            # Return on Equity
            roe = info.get('returnOnEquity', None)
            if roe:
                roe_pct = roe * 100
                if roe_pct > 20:
                    score += 20
                elif roe_pct > 15:
                    score += 15
                elif roe_pct > 10:
                    score += 10
                elif roe_pct < 5:
                    score -= 10
            
            # Profit Margin
            profit_margin = info.get('profitMargins', None)
            if profit_margin:
                margin_pct = profit_margin * 100
                if margin_pct > 20:
                    score += 15
                elif margin_pct > 15:
                    score += 10
                elif margin_pct > 10:
                    score += 5
                elif margin_pct < 5:
                    score -= 10
            
            # Operating Margin
            operating_margin = info.get('operatingMargins', None)
            if operating_margin:
                op_margin_pct = operating_margin * 100
                if op_margin_pct > 20:
                    score += 10
                elif op_margin_pct > 15:
                    score += 5
                elif op_margin_pct < 5:
                    score -= 10
            
            # Return on Assets
            roa = info.get('returnOnAssets', None)
            if roa:
                roa_pct = roa * 100
                if roa_pct > 10:
                    score += 10
                elif roa_pct > 5:
                    score += 5
                elif roa_pct < 2:
                    score -= 5
                    
        except Exception as e:
            print(f"Profitability analysis error: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_financial_health(self, info: Dict, balance_sheet: pd.DataFrame) -> float:
        """Analyze financial health (debt levels, liquidity, etc.)"""
        score = 50
        
        try:
            # Debt to Equity
            de_ratio = info.get('debtToEquity', None)
            if de_ratio:
                if de_ratio < 30:
                    score += 20
                elif de_ratio < 50:
                    score += 15
                elif de_ratio < 100:
                    score += 10
                elif de_ratio > 200:
                    score -= 20
                elif de_ratio > 150:
                    score -= 10
            
            # Current Ratio
            current_ratio = info.get('currentRatio', None)
            if current_ratio:
                if current_ratio > 2:
                    score += 15
                elif current_ratio > 1.5:
                    score += 10
                elif current_ratio > 1:
                    score += 5
                elif current_ratio < 1:
                    score -= 15
            
            # Quick Ratio
            quick_ratio = info.get('quickRatio', None)
            if quick_ratio:
                if quick_ratio > 1.5:
                    score += 10
                elif quick_ratio > 1:
                    score += 5
                elif quick_ratio < 0.5:
                    score -= 10
            
            # Free Cash Flow
            fcf = info.get('freeCashflow', None)
            if fcf and fcf > 0:
                score += 10
            elif fcf and fcf < 0:
                score -= 15
                
        except Exception as e:
            print(f"Financial health analysis error: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_growth(self, info: Dict, financials: pd.DataFrame) -> float:
        """Analyze growth metrics (revenue growth, EPS growth, etc.)"""
        score = 50
        
        try:
            # Revenue Growth
            revenue_growth = info.get('revenueGrowth', None)
            if revenue_growth:
                growth_pct = revenue_growth * 100
                if growth_pct > 20:
                    score += 20
                elif growth_pct > 15:
                    score += 15
                elif growth_pct > 10:
                    score += 10
                elif growth_pct > 5:
                    score += 5
                elif growth_pct < 0:
                    score -= 15
            
            # Earnings Growth
            earnings_growth = info.get('earningsGrowth', None)
            if earnings_growth:
                eg_pct = earnings_growth * 100
                if eg_pct > 25:
                    score += 20
                elif eg_pct > 15:
                    score += 15
                elif eg_pct > 10:
                    score += 10
                elif eg_pct < 0:
                    score -= 15
            
            # EPS Growth (Quarterly)
            eps_growth_q = info.get('earningsQuarterlyGrowth', None)
            if eps_growth_q:
                if eps_growth_q > 0.20:
                    score += 10
                elif eps_growth_q > 0.10:
                    score += 5
                elif eps_growth_q < 0:
                    score -= 10
                    
        except Exception as e:
            print(f"Growth analysis error: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_dividends(self, info: Dict) -> float:
        """Analyze dividend metrics"""
        score = 50
        
        try:
            # Dividend Yield
            div_yield = info.get('dividendYield', None)
            if div_yield:
                yield_pct = div_yield * 100
                if yield_pct > 4:
                    score += 20
                elif yield_pct > 3:
                    score += 15
                elif yield_pct > 2:
                    score += 10
                elif yield_pct > 1:
                    score += 5
            else:
                # No dividend (growth stock)
                score += 5
            
            # Payout Ratio
            payout = info.get('payoutRatio', None)
            if payout:
                if 0.3 < payout < 0.6:
                    score += 15
                elif 0.2 < payout <= 0.3 or 0.6 <= payout < 0.8:
                    score += 10
                elif payout >= 1:
                    score -= 20
                    
        except Exception as e:
            print(f"Dividend analysis error: {e}")
        
        return max(0, min(100, score))
    
    def _extract_key_metrics(self, info: Dict) -> Dict:
        """Extract key financial metrics for display"""
        return {
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'pb_ratio': info.get('priceToBook'),
            'peg_ratio': info.get('pegRatio'),
            'roe': info.get('returnOnEquity'),
            'profit_margin': info.get('profitMargins'),
            'debt_to_equity': info.get('debtToEquity'),
            'current_ratio': info.get('currentRatio'),
            'revenue_growth': info.get('revenueGrowth'),
            'earnings_growth': info.get('earningsGrowth'),
            'dividend_yield': info.get('dividendYield'),
            'sector': info.get('sector'),
            'industry': info.get('industry')
        }


# ==============================================================================
# TESTING
# ==============================================================================

if __name__ == "__main__":
    print("Testing Fundamental Analysis...")
    ticker = "AAPL"
    analyzer = FundamentalAnalyzer(ticker)
    result = analyzer.analyze()
    
    print(f"\n{ticker} Fundamental Analysis:")
    print(f"Score: {result['score']:.2f}/100")
    print(f"Rating: {result['rating']}")
    print(f"\nComponent Scores:")
    for key, value in result['components'].items():
        print(f"  {key}: {value:.2f}")
    print(f"\nKey Metrics:")
    for key, value in result['metrics'].items():
        if value and key not in ['market_cap', 'sector', 'industry']:
            print(f"  {key}: {value}")