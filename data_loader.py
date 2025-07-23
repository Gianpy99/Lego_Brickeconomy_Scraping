"""
Input data handling utilities
"""
import os
import logging
from typing import List, Union
import pandas as pd

from exceptions import DataValidationError

logger = logging.getLogger(__name__)

class DataLoader:
    """Load LEGO codes from various input sources"""
    
    @staticmethod
    def load_from_excel(file_path: str, column_name: str = None) -> List[str]:
        """Load LEGO codes from Excel file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        try:
            df = pd.read_excel(file_path)
            
            # Try to auto-detect column with LEGO codes
            if column_name is None:
                possible_columns = ['Set Code', 'Ref', 'LEGO Code', 'Code', 'Set', 'set_code', 'ref']
                column_name = None
                
                for col in possible_columns:
                    if col in df.columns:
                        column_name = col
                        break
                
                if column_name is None:
                    # Use first column as fallback
                    column_name = df.columns[0]
                    logger.warning(f"Could not auto-detect column, using first column: {column_name}")
            
            if column_name not in df.columns:
                raise DataValidationError(f"Column '{column_name}' not found in Excel file")
            
            # Extract and clean codes
            codes = df[column_name].astype(str).str.strip().tolist()
            # Remove empty or NaN values
            codes = [code for code in codes if code and code.lower() != 'nan']
            
            logger.info(f"Loaded {len(codes)} LEGO codes from {file_path}")
            return codes
            
        except Exception as e:
            raise DataValidationError(f"Error reading Excel file: {str(e)}")
    
    @staticmethod
    def load_from_csv(file_path: str, column_name: str = None) -> List[str]:
        """Load LEGO codes from CSV file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            
            # Try to auto-detect column with LEGO codes
            if column_name is None:
                possible_columns = ['Set Code', 'Ref', 'LEGO Code', 'Code', 'Set', 'set_code', 'ref']
                column_name = None
                
                for col in possible_columns:
                    if col in df.columns:
                        column_name = col
                        break
                
                if column_name is None:
                    column_name = df.columns[0]
                    logger.warning(f"Could not auto-detect column, using first column: {column_name}")
            
            if column_name not in df.columns:
                raise DataValidationError(f"Column '{column_name}' not found in CSV file")
            
            # Extract and clean codes
            codes = df[column_name].astype(str).str.strip().tolist()
            codes = [code for code in codes if code and code.lower() != 'nan']
            
            logger.info(f"Loaded {len(codes)} LEGO codes from {file_path}")
            return codes
            
        except Exception as e:
            raise DataValidationError(f"Error reading CSV file: {str(e)}")
    
    @staticmethod
    def load_from_text(file_path: str) -> List[str]:
        """Load LEGO codes from text file (one per line)"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                codes = [line.strip() for line in file if line.strip()]
            
            logger.info(f"Loaded {len(codes)} LEGO codes from {file_path}")
            return codes
            
        except Exception as e:
            raise DataValidationError(f"Error reading text file: {str(e)}")
    
    @staticmethod
    def load_from_list(codes: Union[List[str], str]) -> List[str]:
        """Load LEGO codes from a list or comma-separated string"""
        if isinstance(codes, str):
            # Split comma-separated string
            codes = [code.strip() for code in codes.split(',') if code.strip()]
        
        if not isinstance(codes, list):
            raise DataValidationError("Codes must be a list or comma-separated string")
        
        # Clean and validate
        clean_codes = []
        for code in codes:
            code = str(code).strip()
            if code and code.lower() != 'nan':
                clean_codes.append(code)
        
        logger.info(f"Loaded {len(clean_codes)} LEGO codes from list")
        return clean_codes
    
    @staticmethod
    def validate_codes(codes: List[str]) -> List[str]:
        """Validate LEGO codes format"""
        valid_codes = []
        invalid_codes = []
        
        for code in codes:
            # Basic validation - LEGO codes are typically alphanumeric
            if code.replace('-', '').replace('_', '').isalnum():
                valid_codes.append(code)
            else:
                invalid_codes.append(code)
        
        if invalid_codes:
            logger.warning(f"Found {len(invalid_codes)} potentially invalid codes: {invalid_codes[:5]}...")
        
        logger.info(f"Validated {len(valid_codes)} valid LEGO codes")
        return valid_codes
