"""
Data models for LEGO set information
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import re

@dataclass
class LegoSetDetails:
    """Data class for LEGO set details"""
    lego_code: str
    official_name: Optional[str] = None
    number_of_pieces: Optional[str] = None
    number_of_minifigs: Optional[str] = None
    released: Optional[str] = None
    retired: Optional[str] = None
    theme: Optional[str] = None
    value_new_sealed: Optional[str] = None
    value_used: Optional[str] = None
    value_range: Optional[str] = None
    retail_price_eur: Optional[str] = None
    retail_price_gbp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def clean_price(self, price_str: Optional[str]) -> Optional[float]:
        """Clean and convert price string to float"""
        if not price_str or price_str == "NA":
            return None
        
        # Remove currency symbols and extract numeric value
        cleaned = re.sub(r'[^\d.,]', '', price_str)
        if not cleaned:
            return None
            
        try:
            # Handle comma as decimal separator
            if ',' in cleaned and '.' in cleaned:
                # Format like 1,234.56
                cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Format like 123,45 (European)
                parts = cleaned.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    cleaned = cleaned.replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            
            return float(cleaned)
        except ValueError:
            return None
    
    def get_clean_prices(self) -> Dict[str, Optional[float]]:
        """Get cleaned price values"""
        return {
            'retail_price_eur': self.clean_price(self.retail_price_eur),
            'retail_price_gbp': self.clean_price(self.retail_price_gbp),
            'value_new_sealed': self.clean_price(self.value_new_sealed),
            'value_used': self.clean_price(self.value_used)
        }
