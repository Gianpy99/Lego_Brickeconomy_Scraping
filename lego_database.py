"""
Enhanced LEGO Database with Images
Creates a comprehensive database with set images and key information
"""

import os
import requests
import time
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from public_scraper import PublicLegoScraper, scrape_lego_codes_fast
from config import Config
from models import LegoSetDetails
import pandas as pd
from PIL import Image
import io

class LegoImageDatabase:
    """Enhanced LEGO scraper that also downloads set images"""
    
    def __init__(self, config: Config):
        self.config = config
        self.images_dir = "lego_images"
        self.database_dir = "lego_database"
        self._setup_directories()
    
    def _setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.database_dir, exist_ok=True)
    
    def download_set_image(self, lego_code: str, image_url: str) -> Optional[str]:
        """Download and save LEGO set image"""
        try:
            if not image_url or image_url == "Not found":
                return None
            
            # Create filename
            filename = f"{lego_code}.jpg"
            filepath = os.path.join(self.images_dir, filename)
            
            # Skip if already exists
            if os.path.exists(filepath):
                return filepath
            
            # Download image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Verify and resize image
            try:
                with Image.open(filepath) as img:
                    # Resize to thumbnail if too large
                    if img.width > 400 or img.height > 400:
                        img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                        img.save(filepath, "JPEG", quality=85)
                
                print(f"    🖼️ Image saved: {filename}")
                return filepath
                
            except Exception as img_error:
                print(f"    ⚠️ Image processing error: {img_error}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return None
                
        except Exception as e:
            print(f"    ❌ Failed to download image: {str(e)}")
            return None

class EnhancedLegoScraper(PublicLegoScraper):
    """Enhanced scraper that extracts images and comprehensive data"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.image_db = LegoImageDatabase(config)
    
    def extract_enhanced_set_data(self, lego_code: str) -> Dict:
        """Extract comprehensive data including image"""
        
        # Get basic data
        details = self.extract_public_set_data(lego_code)
        
        # Convert to dict for easier manipulation
        data = {
            'lego_code': details.lego_code,
            'official_name': details.official_name,
            'number_of_pieces': details.number_of_pieces,
            'number_of_minifigs': details.number_of_minifigs,
            'released': details.released,
            'retired': details.retired,
            'retail_price_eur': details.retail_price_eur,
            'retail_price_gbp': details.retail_price_gbp,
            'value_new_sealed': details.value_new_sealed,
            'value_used': details.value_used,
            'image_url': 'Not found',
            'image_path': 'Not found',
            'theme': 'Not found',
            'subtheme': 'Not found'
        }
        
        # If we found the set, try to extract additional info and image
        if details.official_name != "Not found":
            try:
                # Extract image URL
                image_url = self._extract_image_url()
                if image_url:
                    data['image_url'] = image_url
                    # Download image
                    image_path = self.image_db.download_set_image(lego_code, image_url)
                    if image_path:
                        data['image_path'] = image_path
                
                # Extract theme information
                theme_info = self._extract_theme_info()
                if theme_info:
                    data.update(theme_info)
                
            except Exception as e:
                print(f"    ⚠️ Error extracting enhanced data: {str(e)}")
        
        return data
    
    def _extract_image_url(self) -> Optional[str]:
        """Extract thumbnail image URL from BrickEconomy - optimized for thumbnails"""
        
        # Aspetta che la pagina si carichi
        time.sleep(1)
        
        # Selettori ottimizzati per thumbnail di BrickEconomy
        image_selectors = [
            # Thumbnail specifici - più probabili e veloci
            "//img[contains(@src, 'thumbnail') or contains(@src, 'thumb')][@src]",
            "//img[contains(@src, '.jpg') and string-length(@src) > 30 and string-length(@src) < 200]",
            # Immagini nell'area principale del contenuto
            "//*[@id='ContentPlaceHolder1']//img[@src]",
            # Immagini con dimensioni ragionevoli per thumbnail
            "//img[@width and @height and @src]",
            # Pattern generici ma sicuri
            "//img[contains(@src, '.jpg') and contains(@src, 'http')][@src]",
        ]
        
        for i, selector in enumerate(image_selectors, 1):
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                
                for element in elements[:5]:  # Controlla solo i primi 5 per velocità
                    try:
                        src = element.get_attribute('src')
                        if src and self._is_valid_thumbnail_url(src):
                            print(f"      �️ Thumbnail found (selector {i}): {src[:60]}...")
                            return src
                    except:
                        continue
                        
            except Exception as e:
                continue
        
        print(f"      ❌ No valid thumbnail found")
        return None
    
    def _is_valid_thumbnail_url(self, url: str) -> bool:
        """Quick validation for thumbnail URLs"""
        if not url or len(url) < 20:
            return False
        
        # Must be HTTP/HTTPS
        if not (url.startswith('http://') or url.startswith('https://')):
            return False
        
        # Must have image extension
        if not any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png']):
            return False
        
        # Quick exclude common non-set images
        exclude_terms = ['logo', 'icon', 'button', 'arrow', 'star', 'flag']
        if any(term in url.lower() for term in exclude_terms):
            return False
        
        # Reasonable URL length (not too long = likely valid)
        if len(url) > 300:
            return False
        
        return True
    
    def _extract_theme_info(self) -> Dict:
        """Extract theme and subtheme information with improved selectors"""
        theme_info = {'theme': 'Not found', 'subtheme': 'Not found'}
        
        # More specific theme selectors - avoid navigation elements
        theme_selectors = [
            # Try to find theme in the breadcrumb or set details area
            "//*[@id='ContentPlaceHolder1_SetDetails']//*[contains(text(), 'Theme')]/following-sibling::*[1]",
            # Look for theme in the set information panel
            "//*[@id='ContentPlaceHolder1_PanelSetFacts']//*[contains(text(), 'Theme')]/following-sibling::*[1]",
            # Look for breadcrumb theme links
            "//div[contains(@class, 'breadcrumb')]//a[position()=2]",
            # Try to find theme in specific data areas only
            "//*[@class='set-info' or @class='set-details']//*[contains(text(), 'Theme')]/following-sibling::*[1]",
        ]
        
        for selector in theme_selectors:
            try:
                element = self.wait_and_find_element(By.XPATH, selector, timeout=1)
                if element and element.is_displayed():
                    text = element.text.strip()
                    # Validate it's actually a theme (not navigation)
                    if text and len(text) > 2 and len(text) < 50 and '\n' not in text:
                        # Additional validation - exclude common navigation terms
                        nav_terms = ['browse', 'deals', 'analysis', 'collection', 'sign', 'region', 'menu']
                        if not any(term in text.lower() for term in nav_terms):
                            theme_info['theme'] = text
                            break
            except:
                continue
        
        return theme_info

def create_lego_database(lego_codes: List[str], headless: bool = True) -> pd.DataFrame:
    """Create comprehensive LEGO database with images"""
    
    config = Config()
    config.HEADLESS = headless
    config.WAIT_TIME = 1
    
    print(f"🏗️ CREATING LEGO DATABASE")
    print(f"📦 Processing {len(lego_codes)} sets with images")
    print("=" * 60)
    
    all_data = []
    start_time = time.time()
    
    with EnhancedLegoScraper(config) as scraper:
        for i, code in enumerate(lego_codes, 1):
            print(f"📦 Processing {i}/{len(lego_codes)}: {code}")
            
            try:
                data = scraper.extract_enhanced_set_data(code)
                all_data.append(data)
                
                # Show progress
                if data['official_name'] != "Not found":
                    print(f"  ✅ {data['official_name']}")
                    if data['number_of_pieces']:
                        print(f"     🧩 {data['number_of_pieces']} pieces")
                    if data['theme'] != "Not found":
                        print(f"     🎨 Theme: {data['theme']}")
                else:
                    print(f"  ❌ Not found")
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                # Add empty data to maintain order
                all_data.append({
                    'lego_code': code,
                    'official_name': 'Error',
                    'number_of_pieces': None,
                    'number_of_minifigs': None,
                    'released': None,
                    'retired': None,
                    'retail_price_eur': None,
                    'retail_price_gbp': None,
                    'value_new_sealed': None,
                    'value_used': None,
                    'image_url': 'Error',
                    'image_path': 'Error',
                    'theme': 'Error',
                    'subtheme': 'Error'
                })
            
            # Small delay between requests
            if i < len(lego_codes):
                scraper.driver.get("https://www.brickeconomy.com/")
                time.sleep(0.5)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Add some computed fields
    df['has_image'] = df['image_path'].apply(lambda x: x not in ['Not found', 'Error', None])
    df['pieces_numeric'] = df['number_of_pieces'].apply(lambda x: 
        int(''.join(filter(str.isdigit, str(x)))) if x and str(x).replace(',', '').isdigit() else None
    )
    
    elapsed = time.time() - start_time
    success_count = len(df[df['official_name'].notna() & (df['official_name'] != 'Not found') & (df['official_name'] != 'Error')])
    images_count = len(df[df['has_image'] == True])
    
    print("\n" + "=" * 60)
    print(f"🎯 DATABASE CREATED in {elapsed:.1f} seconds")
    print(f"📊 Success: {success_count}/{len(lego_codes)} sets ({100*success_count/len(lego_codes):.1f}%)")
    print(f"🖼️ Images: {images_count}/{len(lego_codes)} downloaded ({100*images_count/len(lego_codes):.1f}%)")
    
    return df

def export_database(df: pd.DataFrame, format: str = 'all') -> List[str]:
    """Export database in multiple formats"""
    
    timestamp = int(time.time())
    base_filename = f"lego_database_{timestamp}"
    output_files = []
    
    if format in ['excel', 'all']:
        # Excel with multiple sheets
        excel_file = f"lego_database/{base_filename}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Main data
            df.to_excel(writer, sheet_name='LEGO_Sets', index=False)
            
            # Summary by theme
            if 'theme' in df.columns:
                theme_summary = df.groupby('theme').agg({
                    'lego_code': 'count',
                    'pieces_numeric': 'mean',
                    'has_image': 'sum'
                }).round(1)
                theme_summary.columns = ['Sets_Count', 'Avg_Pieces', 'Images_Count']
                theme_summary.to_excel(writer, sheet_name='Themes_Summary')
            
            # Sets with images
            sets_with_images = df[df['has_image'] == True]
            if not sets_with_images.empty:
                sets_with_images.to_excel(writer, sheet_name='Sets_With_Images', index=False)
        
        output_files.append(excel_file)
        print(f"📊 Excel database: {excel_file}")
    
    if format in ['csv', 'all']:
        csv_file = f"lego_database/{base_filename}.csv"
        df.to_csv(csv_file, index=False)
        output_files.append(csv_file)
        print(f"📊 CSV database: {csv_file}")
    
    if format in ['html', 'all']:
        # Create HTML report with images
        html_file = f"lego_database/{base_filename}.html"
        create_html_report(df, html_file)
        output_files.append(html_file)
        print(f"🌐 HTML report: {html_file}")
    
    return output_files

def create_html_report(df: pd.DataFrame, filename: str):
    """Create HTML report with images"""
    import shutil
    
    # Crea cartella images nella stessa directory dell'HTML
    html_dir = os.path.dirname(filename)
    images_dir = os.path.join(html_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LEGO Database Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .set-card { 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 15px; 
                margin: 10px 0; 
                display: flex; 
                align-items: center;
                background: #f9f9f9;
            }
            .set-image { 
                width: 150px; 
                height: 150px; 
                object-fit: contain; 
                margin-right: 20px;
                border: 1px solid #ccc;
                background: white;
            }
            .set-info { flex: 1; }
            .set-title { font-size: 18px; font-weight: bold; color: #2c3e50; }
            .set-details { margin: 5px 0; }
            .not-found { opacity: 0.5; }
            .summary { 
                background: #e8f4f8; 
                padding: 15px; 
                border-radius: 5px; 
                margin-bottom: 20px; 
            }
        </style>
    </head>
    <body>
        <h1>🧱 LEGO Database Report</h1>
    """
    
    # Add summary
    total_sets = len(df)
    found_sets = len(df[df['official_name'].notna() & (df['official_name'] != 'Not found') & (df['official_name'] != 'Error')])
    with_images = len(df[df['has_image'] == True])
    
    html_content += f"""
        <div class="summary">
            <h2>📊 Summary</h2>
            <p><strong>Total Sets:</strong> {total_sets}</p>
            <p><strong>Successfully Found:</strong> {found_sets} ({100*found_sets/total_sets:.1f}%)</p>
            <p><strong>With Images:</strong> {with_images} ({100*with_images/total_sets:.1f}%)</p>
        </div>
        
        <h2>📦 LEGO Sets</h2>
    """
    
    # Add each set
    for _, row in df.iterrows():
        is_found = row['official_name'] not in ['Not found', 'Error', None]
        card_class = "set-card" if is_found else "set-card not-found"
        
        # Image
        if row['has_image'] and os.path.exists(row['image_path']):
            # Copia l'immagine nella cartella images
            image_filename = f"{row['lego_code']}.jpg"
            dest_path = os.path.join(images_dir, image_filename)
            try:
                shutil.copy2(row['image_path'], dest_path)
                # Usa percorso relativo per HTML
                image_src = f"images/{image_filename}"
                image_tag = f'<img src="{image_src}" class="set-image" alt="LEGO {row["lego_code"]}">'
            except Exception as e:
                print(f"⚠️ Errore copia immagine {row['lego_code']}: {e}")
                image_tag = '<div class="set-image" style="display:flex;align-items:center;justify-content:center;color:#999;">Image Error</div>'
        else:
            image_tag = '<div class="set-image" style="display:flex;align-items:center;justify-content:center;color:#999;">No Image</div>'
        
        # Set info
        name = row['official_name'] if is_found else f"Set {row['lego_code']} (Not Found)"
        pieces = f"🧩 {row['number_of_pieces']} pieces" if row['number_of_pieces'] else ""
        minifigs = f"👥 {row['number_of_minifigs']} minifigs" if row['number_of_minifigs'] else ""
        released = f"📅 Released: {row['released']}" if row['released'] and row['released'] != 'Not found' else ""
        price = f"💰 {row['retail_price_eur'] or row['retail_price_gbp']}" if (row['retail_price_eur'] and row['retail_price_eur'] != 'Not found') or (row['retail_price_gbp'] and row['retail_price_gbp'] != 'Not found') else ""
        theme = f"🎨 Theme: {row['theme']}" if row['theme'] and row['theme'] != 'Not found' else ""
        
        html_content += f"""
            <div class="{card_class}">
                {image_tag}
                <div class="set-info">
                    <div class="set-title">{row['lego_code']}: {name}</div>
                    <div class="set-details">{pieces}</div>
                    <div class="set-details">{minifigs}</div>
                    <div class="set-details">{released}</div>
                    <div class="set-details">{price}</div>
                    <div class="set-details">{theme}</div>
                </div>
            </div>
        """
    
    html_content += """
        </body>
    </html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    """Main function to create LEGO database"""
    import sys

    print("🏗️ LEGO DATABASE CREATOR")
    print("Creates comprehensive database with images")
    print("=" * 50)

    # Lista principale di codici (senza punti)
    default_codes = [
        "3920","9469","9470","9471","9472","9473","9474","9476",
        "10237","10316","10333", "30210","30211","30212","30213",
        "30215","30216","40630","40631","40632","40693","40751",
        "50011","71171","71218","71219","71220","79000","79001",
        "79002","79003","79004","79005","79006","79007","79008",
        "79010","79011","79012","79013","79014","79015","79016",
        "79017","79018","5000202","850674","850680","850514",
        "850515","850516","10367"
    ]

    # Codici aggiuntivi ad-hoc (puoi aggiungere qui in futuro)
    extra_codes = [
        # "99999", "12345"  # esempio, aggiungi qui altri codici
    ]

    # Input da terminale o usa default + extra
    if len(sys.argv) > 1:
        codes = [c.strip().replace('.', '') for c in sys.argv[1].split(',')]
    else:
        codes_input = input("Enter LEGO codes (comma-separated) [default list]: ").strip()
        if not codes_input:
            codes = default_codes + extra_codes
            print(f"Using default codes: {', '.join(codes)}")
        else:
            codes = [c.strip().replace('.', '') for c in codes_input.split(',')] + extra_codes

    # Create database
    df = create_lego_database(codes, headless=True)

    # Export in all formats
    output_files = export_database(df, format='all')

    print(f"\n🎉 DATABASE COMPLETE!")
    print(f"📁 Files created: {len(output_files)}")
    for file in output_files:
        print(f"   📄 {file}")

    print(f"\n💡 Open the HTML file to view your LEGO database with images!")

if __name__ == "__main__":
    main()