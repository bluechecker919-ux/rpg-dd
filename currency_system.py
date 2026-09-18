from typing import Dict

class CurrencySystem:
    def __init__(self):
        self.currency_names = {
            'gold': '골드',
            'silver': '실버', 
            'bronze': '브론즈',
            'gems': '보석'
        }
        
        self.currency_exchange_rates = {
            'gold': 1.0,
            'silver': 0.01,  # 100 실버 = 1 골드
            'bronze': 0.001, # 1000 브론즈 = 1 골드
            'gems': 100.0   # 1 보석 = 100 골드
        }
    
    def convert_to_gold(self, amount: int, currency: str) -> float:
        """다른 통화를 골드로 변환"""
        if currency not in self.currency_exchange_rates:
            return 0.0
        return amount * self.currency_exchange_rates[currency]
    
    def format_price(self, gold_price: int) -> Dict[str, int]:
        """골드 가격을 여러 통화로 변환"""
        remaining = gold_price
        
        gold = remaining // 100
        remaining %= 100
        
        silver = remaining // 1
        remaining %= 1
        
        bronze = int(remaining * 1000)
        
        return {
            'gold': gold,
            'silver': silver,
            'bronze': bronze
        }
    
    def format_price_string(self, gold_price: int) -> str:
        """가격을 문자열로 포맷팅"""
        currencies = self.format_price(gold_price)
        
        parts = []
        if currencies['gold'] > 0:
            parts.append(f"{currencies['gold']}🪙")
        if currencies['silver'] > 0:
            parts.append(f"{currencies['silver']}🪙")
        if currencies['bronze'] > 0:
            parts.append(f"{currencies['bronze']}🪙")
        
        return " ".join(parts) if parts else "0🪙"