"""
Main application script for LEGO BrickEconomy scraper
"""
import argparse
import logging
import sys
from typing import List, Optional

from config import Config
from scraper import BrickEconomyScraper
from data_loader import DataLoader
from data_export import DataExporter
from exceptions import BrickEconomyScraperError

def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('scraper.log', encoding='utf-8')
        ]
    )

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Professional LEGO BrickEconomy Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --codes "3920,9469,10333"
  python main.py --excel-file "input.xlsx" --column "Set Code"
  python main.py --csv-file "codes.csv" --output-format json
  python main.py --text-file "codes.txt" --headless --verbose
        """
    )
    
    # Input sources (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--codes', 
        type=str, 
        help='Comma-separated list of LEGO codes'
    )
    input_group.add_argument(
        '--excel-file', 
        type=str, 
        help='Path to Excel file containing LEGO codes'
    )
    input_group.add_argument(
        '--csv-file', 
        type=str, 
        help='Path to CSV file containing LEGO codes'
    )
    input_group.add_argument(
        '--text-file', 
        type=str, 
        help='Path to text file containing LEGO codes (one per line)'
    )
    
    # Optional parameters
    parser.add_argument(
        '--column', 
        type=str, 
        help='Column name containing LEGO codes (for Excel/CSV files)'
    )
    parser.add_argument(
        '--output-format', 
        choices=['xlsx', 'csv', 'json', 'all'], 
        default='xlsx',
        help='Output format (default: xlsx)'
    )
    parser.add_argument(
        '--output-file', 
        type=str, 
        help='Custom output filename (without extension)'
    )
    parser.add_argument(
        '--headless', 
        action='store_true', 
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--fast', 
        action='store_true',
        help='Enable fast mode with aggressive optimizations'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--delay', 
        type=int, 
        default=2,
        help='Delay between requests in seconds (default: 2, use 0.5 for fast mode)'
    )
    
    return parser.parse_args()

def load_lego_codes(args: argparse.Namespace) -> List[str]:
    """Load LEGO codes from specified source"""
    if args.codes:
        return DataLoader.load_from_list(args.codes)
    elif args.excel_file:
        return DataLoader.load_from_excel(args.excel_file, args.column)
    elif args.csv_file:
        return DataLoader.load_from_csv(args.csv_file, args.column)
    elif args.text_file:
        return DataLoader.load_from_text(args.text_file)
    else:
        raise ValueError("No input source specified")

def main():
    """Main application entry point"""
    args = parse_arguments()
    setup_logging(args.verbose)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting LEGO BrickEconomy Scraper v2.0")
    
    try:
        # Validate configuration
        Config.validate()
        
        # Load LEGO codes
        logger.info("Loading LEGO codes...")
        lego_codes = load_lego_codes(args)
        lego_codes = DataLoader.validate_codes(lego_codes)
        
        if not lego_codes:
            logger.error("No valid LEGO codes found")
            return 1
        
        logger.info(f"Loaded {len(lego_codes)} LEGO codes to process")
        
        # Configure scraper with performance options
        config = Config()
        if args.headless or args.fast:
            config.HEADLESS = True
        if args.delay:
            config.SCRAPING_DELAY = args.delay
        
        if args.fast:
            logger.info("🚀 FAST MODE enabled - Using aggressive optimizations")
            config.WAIT_TIME = 1  # Faster waits
            # Reduce logging for speed
            logging.getLogger('scraper').setLevel(logging.WARNING)
        
        # Run scraper
        logger.info("Starting scraping process...")
        with BrickEconomyScraper(config) as scraper:
            results = scraper.scrape_lego_sets(lego_codes)
        
        # Export results
        logger.info("Exporting results...")
        exporter = DataExporter(config)
        
        output_files = []
        
        if args.output_format == 'all':
            formats = ['xlsx', 'csv', 'json']
        else:
            formats = [args.output_format]
        
        for fmt in formats:
            if args.output_file:
                filename = f"{args.output_file}.{fmt}"
            else:
                filename = None
            
            if fmt == 'xlsx':
                output_file = exporter.to_excel(results, filename)
            elif fmt == 'csv':
                output_file = exporter.to_csv(results, filename)
            elif fmt == 'json':
                output_file = exporter.to_json(results, filename)
            
            output_files.append(output_file)
        
        # Generate summary report
        summary_file = exporter.export_summary_report(results)
        output_files.append(summary_file)
        
        logger.info("Scraping completed successfully!")
        logger.info("Output files:")
        for file in output_files:
            logger.info(f"  - {file}")
        
        return 0
        
    except BrickEconomyScraperError as e:
        logger.error(f"Scraper error: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
