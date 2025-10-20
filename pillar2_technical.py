"""
PILLAR 2: TECHNICAL ANALYSIS
Analyzes price patterns and technical indicators

File: pillar2_technical.py
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, Tuple
from datetime import datetime, timedelta

class TechnicalAnalyzer:
    """Analyzes technical indicators and price patterns"""
    
    def __init__(self, ticker: str, lookback_days: int = 252):
        self.ticker = ticker
        self.lookback_days = lookback_days
        self.data = self._fetch_data()
        
    def _fetch_data(self) -> pd.DataFrame:
        """Fetch historical price data"""
        start_date = (datetime.now() - timedelta(days=self.lookback_days + 100)).strftime('%Y-%m-%d')
        stock = yf.Ticker(self.ticker)
        df = stock.history(start=start_date)
        
        if df.empty:
            raise ValueError(f"No data found for {self.ticker}")
        
        return df
    
    def analyze(self) -> Dict:
        """Perform complete technical analysis"""
        
        # Calculate all indicators
        self._calculate_moving_averages()
        self._calculate_rsi()
        self._calculate_macd()
        self._calculate_bollinger_bands()
        self._calculate_volume_analysis()
        
        # Analyze each component
        trend_score = self._analyze_trend()
        momentum_score = self._analyze_momentum()
        volatility_score = self._analyze_volatility()
        volume_score = self._analyze_volume()
        pattern_score = self._analyze_patterns()
        
        # Calculate weighted overall score
        weights = {
            'trend': 0.30,
            'momentum': 0.25,
            'volatility': 0.15,
            'volume': 0.15,
            'patterns': 0.15
        }
        
        total_score = (
            trend_score * weights['trend'] +
            momentum_score * weights['momentum'] +
            volatility_score * weights['volatility'] +
            volume_score * weights['volume'] +
            pattern_score * weights['patterns']
        )
        
        # Get current indicators
        current_indicators = self._get_current_indicators()
        
        # Generate signals
        signals = {
            'trend': self._trend_signal(trend_score),
            'momentum': self._momentum_signal(momentum_score),
            'overall': self._overall_signal(total_score)
        }
        
        return {
            'score': total_score,
            'components': {
                'trend': trend_score,
                'momentum': momentum_score,
                'volatility': volatility_score,
                'volume': volume_score,
                'patterns': pattern_score
            },
            'indicators': current_indicators,
            'signals': signals
        }
    
    def _calculate_moving_averages(self):
        """Calculate various moving averages"""
        self.data['SMA_20'] = self.data['Close'].rolling(window=20).mean()
        self.data['SMA_50'] = self.data['Close'].rolling(window=50).mean()
        self.data['SMA_200'] = self.data['Close'].rolling(window=200).mean()
        self.data['EMA_12'] = self.data['Close'].ewm(span=12, adjust=False).mean()
        self.data['EMA_26'] = self.data['Close'].ewm(span=26, adjust=False).mean()
    
    def _calculate_rsi(self, period: int = 14):
        """Calculate Relative Strength Index"""
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
    
    def _calculate_macd(self):
        """Calculate MACD indicator"""
        self.data['MACD'] = self.data['EMA_12'] - self.data['EMA_26']
        self.data['MACD_Signal'] = self.data['MACD'].ewm(span=9, adjust=False).mean()
        self.data['MACD_Hist'] = self.data['MACD'] - self.data['MACD_Signal']
    
    def _calculate_bollinger_bands(self, period: int = 20):
        """Calculate Bollinger Bands"""
        self.data['BB_Middle'] = self.data['Close'].rolling(window=period).mean()
        std = self.data['Close'].rolling(window=period).std()
        self.data['BB_Upper'] = self.data['BB_Middle'] + (std * 2)
        self.data['BB_Lower'] = self.data['BB_Middle'] - (std * 2)
    
    def _calculate_volume_analysis(self):
        """Calculate volume indicators"""
        self.data['Volume_SMA'] = self.data['Volume'].rolling(window=20).mean()
        self.data['Volume_Ratio'] = self.data['Volume'] / self.data['Volume_SMA']
    
    def _analyze_trend(self) -> float:
        """Analyze price trend"""
        score = 50
        
        try:
            current_price = self.data['Close'].iloc[-1]
            sma_20 = self.data['SMA_20'].iloc[-1]
            sma_50 = self.data['SMA_50'].iloc[-1]
            sma_200 = self.data['SMA_200'].iloc[-1]
            
            # Price vs Moving Averages
            if current_price > sma_20:
                score += 10
            else:
                score -= 10
                
            if current_price > sma_50:
                score += 15
            else:
                score -= 15
                
            if current_price > sma_200:
                score += 20
            else:
                score -= 20
            
            # Moving Average Alignment (Golden Cross / Death Cross)
            if sma_20 > sma_50 > sma_200:
                score += 15  # Strong uptrend
            elif sma_20 < sma_50 < sma_200:
                score -= 15  # Strong downtrend
            
            # Recent trend strength
            returns_20d = (current_price - self.data['Close'].iloc[-20]) / self.data['Close'].iloc[-20]
            if returns_20d > 0.10:
                score += 10
            elif returns_20d > 0.05:
                score += 5
            elif returns_20d < -0.10:
                score -= 10
            elif returns_20d < -0.05:
                score -= 5
                
        except Exception as e:
            print(f"Trend analysis error: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_momentum(self) -> float:
        """Analyze momentum indicators"""
        score = 50
        
        try:
            rsi = self.data['RSI'].iloc[-1]
            macd = self.data['MACD'].iloc[-1]
            macd_signal = self.data['MACD_Signal'].iloc[-1]
            macd_hist = self.data['MACD_Hist'].iloc[-1]
            
            # RSI Analysis
            if 40 < rsi < 60:
                score += 10  # Neutral momentum
            elif 30 < rsi <= 40:
                score += 15  # Oversold - buying opportunity
            elif rsi <= 30:
                score += 20  # Very oversold
            elif 60 <= rsi < 70:
                score += 5   # Overbought but still ok
            elif rsi >= 70:
                score -= 10  # Overbought
            
            # MACD Analysis
            if macd > macd_signal:
                score += 15  # Bullish crossover
            else:
                score -= 10  # Bearish
            
            if macd_hist > 0 and self.data['MACD_Hist'].iloc[-2] < 0:
                score += 15  # Just turned positive
            elif macd_hist < 0 and self.data['MACD_Hist'].iloc[-2] > 0:
                score -= 15  # Just turned negative
            
            # Histogram trend
            if macd_hist > self.data['MACD_Hist'].iloc[-2]:
                score += 5  # Increasing momentum
            else:
                score -= 5  # Decreasing momentum
                
        except Exception as e:
            print(f"Momentum analysis error: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_volatility(self) -> float:
        """Analyze price volatility"""
        score = 50
        
        try:
            current_price = self.data['Close'].iloc[-1]
            bb_upper = self.data['BB_Upper'].iloc[-1]
            bb_lower = self.data['BB_Lower'].iloc[-1]
            bb_middle = self.data['BB_Middle'].iloc[-1]
            
            # Bollinger Band position
            bb_width = bb_upper - bb_lower
            bb_position = (current_price - bb_lower) / bb_width
            
            if 0.3 < bb_position < 0.7:
                score += 15  # Middle of band - normal
            elif bb_position <= 0.2:
                score += 20  # Near lower band - oversold
            elif bb_position >= 0.8:
                score -= 10  # Near upper band - overbought
            
            # Volatility level
            returns = self.data['Close'].pct_change()
            volatility = returns.std() * np.sqrt(252)  # Annualized
            
            if volatility < 0.20:
                score += 10  # Low volatility
            elif volatility < 0.30:
                score += 5   # Moderate volatility
            elif volatility > 0.50:
                score -= 10  # High volatility
                
        except Exception as e:
            print(f"Volatility analysis error: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_volume(self) -> float:
        """Analyze volume patterns"""
        score = 50
        
        try:
            current_volume = self.data['Volume'].iloc[-1]
            volume_sma = self.data['Volume_SMA'].iloc[-1]
            volume_ratio = current_volume / volume_sma
            
            # Price change
            price_change = self.data['Close'].pct_change().iloc[-1]
            
            # Volume confirmation
            if price_change > 0 and volume_ratio > 1.2:
                score += 20  # Strong buying
            elif price_change > 0 and volume_ratio > 1.0:
                score += 10  # Normal buying
            elif price_change < 0 and volume_ratio > 1.2:
                score -= 20  # Strong selling
            elif price_change < 0 and volume_ratio > 1.0:
                score -= 10  # Normal selling
            
            # Recent volume trend
            avg_volume_10d = self.data['Volume'].iloc[-10:].mean()
            avg_volume_50d = self.data['Volume'].iloc[-50:].mean()
            
            if avg_volume_10d > avg_volume_50d * 1.2:
                score += 10  # Increasing interest
            elif avg_volume_10d < avg_volume_50d * 0.8:
                score -= 5   # Decreasing interest
                
        except Exception as e:
            print(f"Volume analysis error: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_patterns(self) -> float:
        """Analyze chart patterns"""
        score = 50
        
        try:
            # Support and Resistance
            recent_data = self.data['Close'].iloc[-60:]
            current_price = self.data['Close'].iloc[-1]
            
            # Find recent high and low
            recent_high = recent_data.max()
            recent_low = recent_data.min()
            
            # Price position
            price_range = recent_high - recent_low
            if price_range > 0:
                position = (current_price - recent_low) / price_range
                
                if position < 0.3:
                    score += 15  # Near support
                elif position > 0.7:
                    score -= 10  # Near resistance
            
            # Higher highs and higher lows (uptrend pattern)
            highs = self.data['High'].iloc[-20:]
            lows = self.data['Low'].iloc[-20:]
            
            if highs.iloc[-1] > highs.iloc[-10] and lows.iloc[-1] > lows.iloc[-10]:
                score += 15  # Uptrend pattern
            elif highs.iloc[-1] < highs.iloc[-10] and lows.iloc[-1] < lows.iloc[-10]:
                score -= 15  # Downtrend pattern
                
        except Exception as e:
            print(f"Pattern analysis error: {e}")
        
        return max(0, min(100, score))
    
    def _get_current_indicators(self) -> Dict:
        """Get current values of all indicators"""
        try:
            return {
                'current_price': round(self.data['Close'].iloc[-1], 2),
                'sma_20': round(self.data['SMA_20'].iloc[-1], 2),
                'sma_50': round(self.data['SMA_50'].iloc[-1], 2),
                'sma_200': round(self.data['SMA_200'].iloc[-1], 2),
                'rsi': round(self.data['RSI'].iloc[-1], 2),
                'macd': round(self.data['MACD'].iloc[-1], 4),
                'macd_signal': round(self.data['MACD_Signal'].iloc[-1], 4),
                'bb_upper': round(self.data['BB_Upper'].iloc[-1], 2),
                'bb_lower': round(self.data['BB_Lower'].iloc[-1], 2),
                'volume_ratio': round(self.data['Volume_Ratio'].iloc[-1], 2)
            }
        except:
            return {}
    
    def _trend_signal(self, score: float) -> str:
        """Generate trend signal"""
        if score >= 70:
            return "STRONG UPTREND"
        elif score >= 55:
            return "UPTREND"
        elif score >= 45:
            return "NEUTRAL"
        elif score >= 30:
            return "DOWNTREND"
        else:
            return "STRONG DOWNTREND"
    
    def _momentum_signal(self, score: float) -> str:
        """Generate momentum signal"""
        if score >= 70:
            return "STRONG POSITIVE"
        elif score >= 55:
            return "POSITIVE"
        elif score >= 45:
            return "NEUTRAL"
        elif score >= 30:
            return "NEGATIVE"
        else:
            return "STRONG NEGATIVE"
    
    def _overall_signal(self, score: float) -> str:
        """Generate overall technical signal"""
        if score >= 70:
            return "STRONG BUY"
        elif score >= 55:
            return "BUY"
        elif score >= 45:
            return "HOLD"
        elif score >= 30:
            return "SELL"
        else:
            return "STRONG SELL"


# ==============================================================================
# TESTING
# ==============================================================================

if __name__ == "__main__":
    print("Testing Technical Analysis...")
    ticker = "AAPL"
    analyzer = TechnicalAnalyzer(ticker)
    result = analyzer.analyze()
    
    print(f"\n{ticker} Technical Analysis:")
    print(f"Score: {result['score']:.2f}/100")
    print(f"\nComponent Scores:")
    for key, value in result['components'].items():
        print(f"  {key}: {value:.2f}")
    print(f"\nSignals:")
    for key, value in result['signals'].items():
        print(f"  {key}: {value}")
    print(f"\nKey Indicators:")
    print(f"  Price: ${result['indicators']['current_price']:.2f}")
    print(f"  RSI: {result['indicators']['rsi']:.2f}")
    print(f"  MACD: {result['indicators']['macd']:.4f}")