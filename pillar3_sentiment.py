"""
PILLAR 3: SENTIMENT ANALYSIS
Analyzes market sentiment from news and social media

File: pillar3_sentiment.py
"""

import yfinance as yf
from typing import Dict
from datetime import datetime, timedelta

class SentimentAnalyzer:
    """Analyzes market sentiment and analyst recommendations"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        
    def analyze(self) -> Dict:
        """Perform complete sentiment analysis"""
        
        # Get all sentiment data
        recommendations = self._analyze_analyst_recommendations()
        news_sentiment = self._analyze_news_sentiment()
        institutional = self._analyze_institutional_holdings()
        insider = self._analyze_insider_activity()
        
        # Calculate weighted score
        weights = {
            'analyst_rec': 0.35,
            'news': 0.25,
            'institutional': 0.25,
            'insider': 0.15
        }
        
        total_score = (
            recommendations['score'] * weights['analyst_rec'] +
            news_sentiment['score'] * weights['news'] +
            institutional['score'] * weights['institutional'] +
            insider['score'] * weights['insider']
        )
        
        # Determine overall sentiment
        if total_score >= 70:
            sentiment = "VERY BULLISH"
        elif total_score >= 55:
            sentiment = "BULLISH"
        elif total_score >= 45:
            sentiment = "NEUTRAL"
        elif total_score >= 30:
            sentiment = "BEARISH"
        else:
            sentiment = "VERY BEARISH"
        
        return {
            'score': total_score,
            'sentiment': sentiment,
            'components': {
                'analyst_recommendations': recommendations['score'],
                'news_sentiment': news_sentiment['score'],
                'institutional_holdings': institutional['score'],
                'insider_activity': insider['score']
            },
            'analyst_recommendations': recommendations,
            'news_summary': news_sentiment,
            'details': {
                'institutional': institutional,
                'insider': insider
            }
        }
    
    def _analyze_analyst_recommendations(self) -> Dict:
        """Analyze analyst recommendations"""
        score = 50
        recommendation = "HOLD"
        
        try:
            rec_data = self.stock.recommendations
            
            if rec_data is not None and not rec_data.empty:
                # Get most recent recommendations (last 3 months)
                recent_recs = rec_data.tail(20)
                
                # Count recommendation types
                buy_count = 0
                hold_count = 0
                sell_count = 0
                
                for _, row in recent_recs.iterrows():
                    rec = str(row['To Grade']).lower()
                    
                    if any(word in rec for word in ['buy', 'outperform', 'overweight', 'positive']):
                        buy_count += 1
                    elif any(word in rec for word in ['sell', 'underperform', 'underweight', 'negative']):
                        sell_count += 1
                    else:
                        hold_count += 1
                
                total = buy_count + hold_count + sell_count
                
                if total > 0:
                    buy_ratio = buy_count / total
                    sell_ratio = sell_count / total
                    
                    # Calculate score based on ratios
                    if buy_ratio > 0.7:
                        score = 85
                        recommendation = "STRONG BUY"
                    elif buy_ratio > 0.5:
                        score = 70
                        recommendation = "BUY"
                    elif sell_ratio > 0.5:
                        score = 30
                        recommendation = "SELL"
                    elif sell_ratio > 0.3:
                        score = 40
                        recommendation = "HOLD/SELL"
                    else:
                        score = 55
                        recommendation = "HOLD"
                    
                    return {
                        'score': score,
                        'recommendation': recommendation,
                        'buy_count': buy_count,
                        'hold_count': hold_count,
                        'sell_count': sell_count,
                        'buy_ratio': round(buy_ratio * 100, 1),
                        'total_analysts': total
                    }
            
            # If no data, return neutral
            return {
                'score': 50,
                'recommendation': 'HOLD',
                'buy_count': 0,
                'hold_count': 0,
                'sell_count': 0,
                'buy_ratio': 0,
                'total_analysts': 0
            }
                    
        except Exception as e:
            print(f"Analyst recommendation error: {e}")
            return {
                'score': 50,
                'recommendation': 'HOLD',
                'buy_count': 0,
                'hold_count': 0,
                'sell_count': 0,
                'buy_ratio': 0,
                'total_analysts': 0
            }
    
    def _analyze_news_sentiment(self) -> Dict:
        """Analyze news sentiment"""
        score = 50
        
        try:
            # Get recent news
            news = self.stock.news
            
            if news:
                # Simple sentiment based on news headlines
                positive_words = ['up', 'rise', 'gain', 'beat', 'surge', 'bull', 'high', 'growth', 
                                 'profit', 'strong', 'buy', 'upgrade', 'positive', 'outperform']
                negative_words = ['down', 'fall', 'drop', 'miss', 'decline', 'bear', 'low', 'loss',
                                 'weak', 'sell', 'downgrade', 'negative', 'underperform', 'concern']
                
                positive_count = 0
                negative_count = 0
                
                for article in news[:10]:  # Check last 10 news items
                    title = article.get('title', '').lower()
                    
                    pos_score = sum(1 for word in positive_words if word in title)
                    neg_score = sum(1 for word in negative_words if word in title)
                    
                    if pos_score > neg_score:
                        positive_count += 1
                    elif neg_score > pos_score:
                        negative_count += 1
                
                total = positive_count + negative_count
                
                if total > 0:
                    sentiment_ratio = (positive_count - negative_count) / total
                    score = 50 + (sentiment_ratio * 40)  # Scale to 10-90 range
                
                return {
                    'score': max(10, min(90, score)),
                    'positive_count': positive_count,
                    'negative_count': negative_count,
                    'news_count': len(news[:10])
                }
            
            return {
                'score': 50,
                'positive_count': 0,
                'negative_count': 0,
                'news_count': 0
            }
                    
        except Exception as e:
            print(f"News sentiment error: {e}")
            return {
                'score': 50,
                'positive_count': 0,
                'negative_count': 0,
                'news_count': 0
            }
    
    def _analyze_institutional_holdings(self) -> Dict:
        """Analyze institutional investor activity"""
        score = 50
        
        try:
            institutional = self.stock.institutional_holders
            
            if institutional is not None and not institutional.empty:
                # Get major shareholders
                major_holders = self.stock.major_holders
                
                if major_holders is not None and not major_holders.empty:
                    # Get institutional ownership percentage
                    inst_pct = float(major_holders.iloc[0, 0].strip('%'))
                    
                    # Higher institutional ownership often indicates confidence
                    if inst_pct > 80:
                        score = 75
                    elif inst_pct > 60:
                        score = 65
                    elif inst_pct > 40:
                        score = 55
                    elif inst_pct < 20:
                        score = 40
                    
                    return {
                        'score': score,
                        'institutional_pct': inst_pct,
                        'num_institutions': len(institutional)
                    }
            
            return {
                'score': 50,
                'institutional_pct': 0,
                'num_institutions': 0
            }
                    
        except Exception as e:
            print(f"Institutional holdings error: {e}")
            return {
                'score': 50,
                'institutional_pct': 0,
                'num_institutions': 0
            }
    
    def _analyze_insider_activity(self) -> Dict:
        """Analyze insider trading activity"""
        score = 50
        
        try:
            insider_trades = self.stock.insider_transactions
            
            if insider_trades is not None and not insider_trades.empty:
                # Analyze recent insider trades (last 6 months)
                recent_trades = insider_trades.head(20)
                
                buys = 0
                sells = 0
                
                for _, trade in recent_trades.iterrows():
                    if 'Sale' in str(trade.get('Transaction', '')):
                        sells += 1
                    elif 'Buy' in str(trade.get('Transaction', '')):
                        buys += 1
                
                # Insider buying is bullish, selling is bearish (but less significant)
                if buys > sells * 2:
                    score = 70  # Strong buying
                elif buys > sells:
                    score = 60  # More buying
                elif sells > buys * 3:
                    score = 40  # Heavy selling
                elif sells > buys:
                    score = 45  # More selling
                
                return {
                    'score': score,
                    'insider_buys': buys,
                    'insider_sells': sells,
                    'recent_transactions': len(recent_trades)
                }
            
            return {
                'score': 50,
                'insider_buys': 0,
                'insider_sells': 0,
                'recent_transactions': 0
            }
                    
        except Exception as e:
            print(f"Insider activity error: {e}")
            return {
                'score': 50,
                'insider_buys': 0,
                'insider_sells': 0,
                'recent_transactions': 0
            }


# ==============================================================================
# TESTING
# ==============================================================================

if __name__ == "__main__":
    print("Testing Sentiment Analysis...")
    ticker = "AAPL"
    analyzer = SentimentAnalyzer(ticker)
    result = analyzer.analyze()
    
    print(f"\n{ticker} Sentiment Analysis:")
    print(f"Score: {result['score']:.2f}/100")
    print(f"Sentiment: {result['sentiment']}")
    print(f"\nComponent Scores:")
    for key, value in result['components'].items():
        print(f"  {key}: {value:.2f}")
    print(f"\nAnalyst Recommendations:")
    print(f"  Recommendation: {result['analyst_recommendations']['recommendation'].upper()}")
    print(f"  Buy Count: {result['analyst_recommendations']['buy_count']}")
    print(f"  Hold Count: {result['analyst_recommendations']['hold_count']}")
    print(f"  Sell Count: {result['analyst_recommendations']['sell_count']}")