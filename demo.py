#!/usr/bin/env python3
"""
LEGO BrickEconomy Professional Scraper - Interactive Demo
========================================================

A comprehensive demonstration of the professional LEGO BrickEconomy scraper
with all examples and functionality in a single, executable Python file.

Usage:
    python demo.py

This script will guide you through:
1. Environment setup and validation
2. Basic scraping examples
3. Data loading from files
4. Data export in multiple formats
5. Data analysis and visualization

Author: Professional Scraper v2.0
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from scraper import BrickEconomyScraper
    from data_loader import DataLoader
    from data_export import DataExporter
    from config import Config
    from models import LegoSetDetails
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required modules are present and dependencies are installed.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('demo.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class LegoScraperDemo:
    """Interactive demonstration of the LEGO BrickEconomy scraper"""
    
    def __init__(self):
        self.results: Optional[Dict[str, LegoSetDetails]] = None
        self.sample_file = 'sample_lego_codes.xlsx'
        
    def print_section(self, title: str, symbol: str = "="):
        """Print a formatted section header"""
        print(f"\n{symbol * 60}")
        print(f"  {title}")
        print(f"{symbol * 60}")
        
    def print_step(self, step: str, description: str):
        """Print a formatted step"""
        print(f"\n🔹 {step}")
        print(f"   {description}")
        
    def wait_for_user(self, message: str = "Press Enter to continue..."):
        """Wait for user input"""
        try:
            input(f"\n{message}")
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user. Goodbye!")
            sys.exit(0)
    
    def setup_environment(self):
        """Step 1: Environment setup and validation"""
        self.print_section("1. ENVIRONMENT SETUP", "🚀")
        
        print("Setting up the professional LEGO BrickEconomy scraper environment...")
        
        # Create .env file if it doesn't exist
        if not os.path.exists('.env'):
            with open('.env', 'w') as f:
                f.write("""# Environment variables for the LEGO BrickEconomy Scraper
BRICKECONOMY_USERNAME=your_username_here
BRICKECONOMY_PASSWORD=your_password_here
CHROME_HEADLESS=false
SCRAPING_DELAY=2
OUTPUT_FORMAT=xlsx
""")
            print("✅ Created .env file")
            print(f"📁 File location: {os.path.abspath('.env')}")
            print("\n⚠️  IMPORTANT: Please edit the .env file with your BrickEconomy credentials before continuing!")
            self.wait_for_user("After setting up your credentials, press Enter to continue...")
        else:
            print("✅ .env file already exists")
        
        # Load environment variables
        load_dotenv()
        
        # Validate credentials
        username = os.getenv("BRICKECONOMY_USERNAME", "")
        password = os.getenv("BRICKECONOMY_PASSWORD", "")
        
        if username == "your_username_here" or not username:
            print("⚠️  Warning: Please set your BRICKECONOMY_USERNAME in the .env file")
        if password == "your_password_here" or not password:
            print("⚠️  Warning: Please set your BRICKECONOMY_PASSWORD in the .env file")
        
        if username and password and username != "your_username_here" and password != "your_password_here":
            print("✅ Environment configured successfully!")
            return True
        else:
            print("❌ Environment not properly configured")
            return False
    
    def demonstrate_basic_usage(self):
        """Step 2: Basic scraping demonstration"""
        self.print_section("2. BASIC SCRAPING EXAMPLE", "📦")
        
        print("Let's start with a simple example - scraping a single LEGO set.")
        
        lego_codes = ["3920"]  # Example LEGO code
        print(f"Target LEGO code: {lego_codes[0]} (Rock Raiders Crystal Sweeper)")
        
        self.wait_for_user("Press Enter to start scraping...")
        
        try:
            # Validate configuration
            Config.validate()
            print("✅ Configuration validated")
            
            # Scrape the data
            print(f"🚀 Starting scraping process for {len(lego_codes)} LEGO set...")
            
            with BrickEconomyScraper() as scraper:
                results = scraper.scrape_lego_sets(lego_codes)
            
            # Display results
            for code, details in results.items():
                print(f"\n📋 LEGO Set {code} Results:")
                print(f"   📛 Name: {details.official_name}")
                print(f"   🧩 Pieces: {details.number_of_pieces}")
                print(f"   👥 Minifigs: {details.number_of_minifigs}")
                print(f"   📅 Released: {details.released}")
                print(f"   🏪 Retail Price (EUR): {details.retail_price_eur}")
                print(f"   💰 Current Value: {details.value_new_sealed}")
                print(f"   📈 Used Value: {details.value_used}")
            
            print(f"\n✅ Successfully scraped {len(results)} LEGO set!")
            return results
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Make sure you have set up your credentials correctly!")
            return None
    
    def create_sample_data(self):
        """Create sample Excel file for demonstration"""
        sample_data = {
            'Set Code': ['3920', '9469', '10333', '9470', '40632'],
            'Description': [
                'LEGO Rock Raiders Crystal Sweeper',
                'LEGO Lord of the Rings Gandalf Arrives',
                'LEGO Icons Typewriter',
                'LEGO Lord of the Rings Shelob Attacks',
                'LEGO BrickHeadz Homer Simpson & Krusty the Clown'
            ],
            'Theme': [
                'Rock Raiders',
                'Lord of the Rings',
                'Icons',
                'Lord of the Rings',
                'BrickHeadz'
            ]
        }
        
        df_sample = pd.DataFrame(sample_data)
        df_sample.to_excel(self.sample_file, index=False)
        return df_sample
    
    def demonstrate_data_loading(self):
        """Step 3: Data loading capabilities"""
        self.print_section("3. DATA LOADING CAPABILITIES", "📁")
        
        print("The scraper can load LEGO codes from multiple sources:")
        
        # Create sample file
        print("Creating sample Excel file...")
        df_sample = self.create_sample_data()
        print(f"✅ Created {self.sample_file} with {len(df_sample)} LEGO sets")
        
        print(f"\n📊 Sample data:")
        print(df_sample.to_string(index=False))
        
        print(f"\n🔍 Demonstrating different data loading methods:")
        
        # Method 1: From Excel file
        try:
            codes_from_excel = DataLoader.load_from_excel(self.sample_file, 'Set Code')
            print(f"✅ Excel file: Loaded {len(codes_from_excel)} codes")
            print(f"   Codes: {codes_from_excel}")
        except Exception as e:
            print(f"❌ Excel loading error: {e}")
            codes_from_excel = []
        
        # Method 2: From string
        codes_from_string = DataLoader.load_from_list("3920,9469,10333")
        print(f"✅ String input: Loaded {len(codes_from_string)} codes")
        print(f"   Codes: {codes_from_string}")
        
        # Method 3: From list
        codes_from_list = DataLoader.load_from_list(['3920', '9469', '10333'])
        print(f"✅ List input: Loaded {len(codes_from_list)} codes")
        print(f"   Codes: {codes_from_list}")
        
        # Validate codes
        if codes_from_excel:
            validated_codes = DataLoader.validate_codes(codes_from_excel)
            print(f"✅ Validation: {len(validated_codes)} valid codes")
            return validated_codes
        
        return codes_from_string
    
    def demonstrate_comprehensive_scraping(self):
        """Step 4: Comprehensive scraping and export"""
        self.print_section("4. COMPREHENSIVE SCRAPING & EXPORT", "🏭")
        
        print("Now let's scrape multiple LEGO sets and export the results in different formats.")
        
        # Load codes from sample file
        try:
            lego_codes = DataLoader.load_from_excel(self.sample_file, 'Set Code')
            print(f"📦 Processing {len(lego_codes)} LEGO sets: {lego_codes}")
        except Exception as e:
            print(f"❌ Could not load from Excel: {e}")
            lego_codes = ['3920', '9469', '10333']
            print(f"📦 Using fallback codes: {lego_codes}")
        
        print("\n⚠️  This will take a few minutes as we scrape multiple sets...")
        self.wait_for_user("Press Enter to start comprehensive scraping...")
        
        try:
            # Configure scraper
            config = Config()
            config.SCRAPING_DELAY = 2  # Be respectful to the website
            
            # Scrape the data
            print("🚀 Starting comprehensive scraping...")
            with BrickEconomyScraper(config) as scraper:
                results = scraper.scrape_lego_sets(lego_codes)
            
            print(f"✅ Successfully scraped {len(results)} sets!")
            
            # Store results for analysis
            self.results = results
            
            # Export data
            print("\n📊 Exporting data to multiple formats...")
            exporter = DataExporter(config)
            
            # Export to Excel
            excel_file = exporter.to_excel(results, "demo_results.xlsx")
            print(f"✅ Excel: {excel_file}")
            
            # Export to CSV
            csv_file = exporter.to_csv(results, "demo_results.csv")
            print(f"✅ CSV: {csv_file}")
            
            # Export to JSON
            json_file = exporter.to_json(results, "demo_results.json")
            print(f"✅ JSON: {json_file}")
            
            # Generate summary report
            summary_file = exporter.export_summary_report(results, "demo_summary.txt")
            print(f"✅ Summary: {summary_file}")
            
            # Display sample results
            print(f"\n📋 Sample Results (first 3 sets):")
            for code, details in list(results.items())[:3]:
                print(f"\n🔹 {code} - {details.official_name}")
                print(f"   🧩 Pieces: {details.number_of_pieces}")
                print(f"   📅 Released: {details.released}")
                if details.retail_price_eur != "NA":
                    print(f"   🏪 Retail Price: {details.retail_price_eur}")
                if details.value_new_sealed != "NA":
                    print(f"   💰 Current Value: {details.value_new_sealed}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error during comprehensive scraping: {str(e)}")
            return None
    
    def demonstrate_data_analysis(self):
        """Step 5: Data analysis and insights"""
        self.print_section("5. DATA ANALYSIS & INSIGHTS", "📈")
        
        if not self.results:
            print("⚠️  No data available for analysis. Skipping this step.")
            return
        
        print("Analyzing the scraped data to extract insights...")
        
        try:
            # Convert to DataFrame for analysis
            analysis_data = []
            for code, details in self.results.items():
                clean_prices = details.get_clean_prices()
                
                row = {
                    'lego_code': code,
                    'name': details.official_name,
                    'pieces': details.number_of_pieces,
                    'released': details.released,
                    'retail_price_eur': clean_prices['retail_price_eur'],
                    'current_value': clean_prices['value_new_sealed'],
                    'used_value': clean_prices['value_used']
                }
                analysis_data.append(row)
            
            df_analysis = pd.DataFrame(analysis_data)
            
            # Basic statistics
            print(f"\n📊 Analysis Summary:")
            print(f"   📦 Total sets analyzed: {len(df_analysis)}")
            print(f"   💰 Sets with price data: {df_analysis['retail_price_eur'].notna().sum()}")
            print(f"   📈 Sets with current value: {df_analysis['current_value'].notna().sum()}")
            
            # Calculate value changes
            df_analysis['value_change'] = df_analysis['current_value'] - df_analysis['retail_price_eur']
            df_analysis['value_change_pct'] = (df_analysis['value_change'] / df_analysis['retail_price_eur']) * 100
            
            # Find valuable sets
            valuable_sets = df_analysis[
                df_analysis['value_change'].notna() & 
                (df_analysis['value_change'] > 0)
            ].sort_values('value_change_pct', ascending=False)
            
            if not valuable_sets.empty:
                print(f"\n💎 Sets with Value Appreciation:")
                for _, row in valuable_sets.head(3).iterrows():
                    if pd.notna(row['retail_price_eur']) and pd.notna(row['current_value']):
                        print(f"   🔹 {row['lego_code']}: {row['name']}")
                        print(f"      💰 Retail: €{row['retail_price_eur']:.2f} → Current: €{row['current_value']:.2f}")
                        print(f"      📈 Gain: €{row['value_change']:.2f} ({row['value_change_pct']:.1f}%)")
            
            # Price statistics
            valid_prices = df_analysis['retail_price_eur'].dropna()
            valid_values = df_analysis['current_value'].dropna()
            
            if len(valid_prices) > 0:
                print(f"\n💰 Price Statistics:")
                print(f"   📊 Average Retail Price: €{valid_prices.mean():.2f}")
                print(f"   📊 Price Range: €{valid_prices.min():.2f} - €{valid_prices.max():.2f}")
            
            if len(valid_values) > 0:
                print(f"   📈 Average Current Value: €{valid_values.mean():.2f}")
                print(f"   📈 Value Range: €{valid_values.min():.2f} - €{valid_values.max():.2f}")
            
            # Display detailed data
            print(f"\n📋 Detailed Analysis Data:")
            display_cols = ['lego_code', 'name', 'retail_price_eur', 'current_value', 'value_change_pct']
            available_cols = [col for col in display_cols if col in df_analysis.columns]
            print(df_analysis[available_cols].to_string(index=False, float_format='%.2f'))
            
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
    
    def show_command_line_usage(self):
        """Step 6: Command line usage examples"""
        self.print_section("6. COMMAND LINE USAGE", "💻")
        
        print("The scraper also provides a powerful command-line interface:")
        print("\n📝 Example Commands:")
        
        examples = [
            ("Basic usage", 'python main.py --codes "3920"'),
            ("From Excel file", f'python main.py --excel-file "{self.sample_file}" --column "Set Code"'),
            ("Export all formats", 'python main.py --codes "3920,9469" --output-format all'),
            ("Headless mode", 'python main.py --codes "3920" --headless --verbose'),
            ("Custom delay", 'python main.py --codes "3920" --delay 3'),
            ("Custom output", 'python main.py --codes "3920" --output-file "my_data"'),
        ]
        
        for desc, cmd in examples:
            print(f"\n🔹 {desc}:")
            print(f"   {cmd}")
        
        print(f"\n📚 For full help: python main.py --help")
    
    def show_project_structure(self):
        """Show the project structure and key improvements"""
        self.print_section("7. PROJECT STRUCTURE & IMPROVEMENTS", "🏗️")
        
        print("Professional scraper architecture:")
        
        structure = """
📁 Project Structure:
├── main.py              # Command-line interface
├── scraper.py           # Core scraping logic
├── config.py            # Configuration management
├── models.py            # Data models
├── data_loader.py       # Input handling
├── data_export.py       # Output handling
├── exceptions.py        # Custom exceptions
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
├── demo.py             # This demonstration
└── README.md           # Documentation
        """
        
        print(structure)
        
        print("\n✅ Key Improvements Over Original:")
        improvements = [
            "Modular Design - Separated concerns into logical modules",
            "Error Handling - Comprehensive exception handling and recovery",
            "Configuration - Environment-based configuration with validation",
            "Data Models - Structured data classes with validation",
            "Multiple Formats - Excel, CSV, JSON export with summary reports",
            "Logging System - Detailed logging with multiple levels",
            "Context Managers - Automatic resource cleanup",
            "Data Validation - Input/output data validation and cleaning",
            "Command Line Interface - Professional CLI with help",
            "Documentation - Comprehensive docstrings and README"
        ]
        
        for improvement in improvements:
            print(f"   ✅ {improvement}")
    
    def run_demo(self):
        """Run the complete demonstration"""
        print("🎉 Welcome to the LEGO BrickEconomy Professional Scraper Demo!")
        print("This interactive demonstration will guide you through all the features.")
        
        try:
            # Step 1: Environment setup
            if not self.setup_environment():
                print("\n❌ Cannot continue without proper environment setup.")
                print("Please configure your credentials in the .env file and try again.")
                return
            
            self.wait_for_user()
            
            # Step 2: Basic usage
            basic_results = self.demonstrate_basic_usage()
            self.wait_for_user()
            
            # Step 3: Data loading
            self.demonstrate_data_loading()
            self.wait_for_user()
            
            # Step 4: Comprehensive scraping
            print("\n🤔 Would you like to run the comprehensive scraping demo?")
            print("This will scrape multiple LEGO sets and may take several minutes.")
            choice = input("Enter 'y' to continue or any other key to skip: ").lower().strip()
            
            if choice == 'y':
                comprehensive_results = self.demonstrate_comprehensive_scraping()
                self.wait_for_user()
                
                # Step 5: Data analysis
                self.demonstrate_data_analysis()
                self.wait_for_user()
            else:
                print("⏭️  Skipping comprehensive scraping demo.")
            
            # Step 6: Command line usage
            self.show_command_line_usage()
            self.wait_for_user()
            
            # Step 7: Project structure
            self.show_project_structure()
            
            # Conclusion
            self.print_section("🎉 DEMO COMPLETED!", "🌟")
            print("Congratulations! You've seen all the features of the professional scraper.")
            print("\n🚀 Next Steps:")
            print("   1. Configure your credentials in the .env file")
            print("   2. Try the command-line interface: python main.py --help")
            print("   3. Customize the configuration in config.py")
            print("   4. Add more LEGO themes to TARGET_THEMES")
            print("   5. Implement additional analysis as needed")
            
            print("\n⚠️  Remember to respect BrickEconomy's terms of service!")
            print("Thank you for using the LEGO BrickEconomy Professional Scraper! 🧱")
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user. Goodbye!")
        except Exception as e:
            print(f"\n❌ Unexpected error during demo: {str(e)}")
            logger.exception("Demo error")

def main():
    """Main entry point"""
    demo = LegoScraperDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
