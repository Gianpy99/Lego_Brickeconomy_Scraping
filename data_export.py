"""
Data export utilities for LEGO set information
"""
import os
import json
import csv
import logging
from typing import Dict, List
from datetime import datetime
import pandas as pd

from models import LegoSetDetails
from config import Config

logger = logging.getLogger(__name__)

class DataExporter:
    """Export scraped LEGO data to various formats"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.ensure_output_directory()
    
    def ensure_output_directory(self) -> None:
        """Ensure output directory exists"""
        if not os.path.exists(self.config.OUTPUT_DIRECTORY):
            os.makedirs(self.config.OUTPUT_DIRECTORY)
            logger.info(f"Created output directory: {self.config.OUTPUT_DIRECTORY}")
    
    def generate_filename(self, base_name: str, extension: str) -> str:
        """Generate timestamped filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(
            self.config.OUTPUT_DIRECTORY,
            f"{base_name}_{timestamp}.{extension}"
        )
    
    def to_excel(self, data: Dict[str, LegoSetDetails], filename: str = None) -> str:
        """Export data to Excel format"""
        if filename is None:
            filename = self.generate_filename("lego_sets", "xlsx")
        
        # Convert to list of dictionaries
        records = []
        for lego_code, details in data.items():
            record = details.to_dict()
            # Add cleaned price columns
            clean_prices = details.get_clean_prices()
            for price_type, value in clean_prices.items():
                record[f"{price_type}_cleaned"] = value
            records.append(record)
        
        # Create DataFrame and export
        df = pd.DataFrame(records)
        df.to_excel(filename, index=False, engine='openpyxl')
        
        logger.info(f"Exported {len(records)} records to Excel: {filename}")
        return filename
    
    def to_csv(self, data: Dict[str, LegoSetDetails], filename: str = None) -> str:
        """Export data to CSV format"""
        if filename is None:
            filename = self.generate_filename("lego_sets", "csv")
        
        # Convert to list of dictionaries
        records = []
        for lego_code, details in data.items():
            record = details.to_dict()
            # Add cleaned price columns
            clean_prices = details.get_clean_prices()
            for price_type, value in clean_prices.items():
                record[f"{price_type}_cleaned"] = value
            records.append(record)
        
        if not records:
            logger.warning("No data to export")
            return filename
        
        # Write CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = records[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        
        logger.info(f"Exported {len(records)} records to CSV: {filename}")
        return filename
    
    def to_json(self, data: Dict[str, LegoSetDetails], filename: str = None) -> str:
        """Export data to JSON format"""
        if filename is None:
            filename = self.generate_filename("lego_sets", "json")
        
        # Convert to serializable format
        json_data = {}
        for lego_code, details in data.items():
            json_data[lego_code] = details.to_dict()
        
        # Add metadata
        export_data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "total_sets": len(json_data),
                "scraper_version": "2.0"
            },
            "data": json_data
        }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(json_data)} records to JSON: {filename}")
        return filename
    
    def export_summary_report(self, data: Dict[str, LegoSetDetails], filename: str = None) -> str:
        """Generate a summary report of the scraped data"""
        if filename is None:
            filename = self.generate_filename("summary_report", "txt")
        
        total_sets = len(data)
        successful_scrapes = sum(1 for details in data.values() if details.official_name and details.official_name != "NA")
        
        # Calculate statistics
        themes = {}
        avg_pieces = []
        avg_prices = []
        
        for details in data.values():
            if details.official_name and details.official_name != "NA":
                # Count themes (would need to extract from search results)
                if details.number_of_pieces and details.number_of_pieces != "NA":
                    try:
                        pieces = int(details.number_of_pieces.replace(',', ''))
                        avg_pieces.append(pieces)
                    except:
                        pass
                
                # Calculate average prices
                clean_prices = details.get_clean_prices()
                if clean_prices['retail_price_eur']:
                    avg_prices.append(clean_prices['retail_price_eur'])
        
        # Generate report
        with open(filename, 'w', encoding='utf-8') as report:
            report.write("LEGO BrickEconomy Scraping Report\n")
            report.write("=" * 40 + "\n\n")
            report.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            report.write(f"Total Sets Processed: {total_sets}\n")
            report.write(f"Successfully Scraped: {successful_scrapes}\n")
            report.write(f"Success Rate: {(successful_scrapes/total_sets*100):.1f}%\n\n")
            
            if avg_pieces:
                report.write(f"Average Piece Count: {sum(avg_pieces)/len(avg_pieces):.0f}\n")
            
            if avg_prices:
                report.write(f"Average Retail Price: €{sum(avg_prices)/len(avg_prices):.2f}\n")
            
            report.write("\nTarget Themes:\n")
            for theme in self.config.TARGET_THEMES:
                report.write(f"  - {theme}\n")
        
        logger.info(f"Generated summary report: {filename}")
        return filename
