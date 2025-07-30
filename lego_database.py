"""
Enhanced LEGO Database with Images
Creates a comprehensive database with set images and key information
"""

import os
import requests
import time
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from public_scraper import PublicLegoScraper
from config import Config
import pandas as pd
import sqlite3
from PIL import Image


class LegoImageDatabase:
    """Enhanced LEGO scraper that also downloads set images"""
    
    def __init__(self, config: Config):
        self.config = config
        self.images_dir = os.path.join("lego_database", "images")  # <-- usa solo questa cartella
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
            
            filename = f"{lego_code}.jpg"
            filepath = os.path.join(self.images_dir, filename)
            
            if os.path.exists(filepath):
                return filepath
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Verifica e ridimensiona SOLO se troppo grande
            try:
                with Image.open(filepath) as img:
                    # Ridimensiona solo se > 1200px
                    if img.width > 1200 or img.height > 1200:
                        img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                        img.save(filepath, "JPEG", quality=95)
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
        """Extract high-quality image URL from BrickEconomy, fallback to thumbnail"""
        time.sleep(0.1)
        # Prima cerca immagini grandi
        image_selectors = [
            "//img[contains(@src, '/resources/images/sets/') and not(contains(@src, 'thumb')) and not(contains(@src, 'thumbnail'))]",
            "//img[contains(@src, '.jpg') and string-length(@src) > 30 and string-length(@src) < 200]",
            "//img[contains(@src, '/sets/') and contains(@src, '.jpg')]",
            "//img[@src and (contains(@src, 'lego-') or contains(@src, 'set-')) and not(contains(@src, 'thumb'))]",
        ]
        # Se non trova nulla, cerca thumbnail
        fallback_selectors = [
            "//img[contains(@src, 'thumbnail') or contains(@src, 'thumb')][@src]",
            "//img[contains(@src, '.jpg') and contains(@src, 'http')][@src]",
        ]
        # Prova prima con immagini grandi
        for i, selector in enumerate(image_selectors, 1):
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements[:3]:
                    src = element.get_attribute('src')
                    if src and self._is_valid_thumbnail_url(src):
                        print(f"      🖼️ High-quality image found (selector {i}): {src[:60]}...")
                        return src
            except:
                continue
        # Fallback ai thumbnail
        for i, selector in enumerate(fallback_selectors, 1):
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements[:3]:
                    src = element.get_attribute('src')
                    if src and self._is_valid_thumbnail_url(src):
                        print(f"      🖼️ Thumbnail found (selector {i}): {src[:60]}...")
                        return src
            except:
                continue
        print(f"      ❌ No valid image found")
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
    config.WAIT_TIME = 0.1
    
    print(f"🏗️ CREATING LEGO DATABASE")
    print(f"📦 Processing {len(lego_codes)} sets with images")
    print("=" * 60)
    
    all_data = []
    start_time = time.time()
        # Carica i codici già presenti
    existing_codes = get_existing_lego_codes()

    with EnhancedLegoScraper(config) as scraper:
        for i, code in enumerate(lego_codes, 1):
            if code in existing_codes:
                print(f"⏩ {code} già presente nel database, salto scraping.")
                continue
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
                time.sleep(0.1)
    
    # Se non ci sono nuovi dati, carica dal database
    if not all_data:
        print("ℹ️ Tutti i codici sono già presenti nel database. Carico i dati da SQLite.")
        conn = sqlite3.connect("lego_database/LegoDatabase.db")
        df = pd.read_sql_query("SELECT * FROM lego_sets", conn)
        conn.close()
    else:
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
    """Export database in multiple formats, always overwriting LegoDatabase files"""
    base_filename = f"lego_database/LegoDatabase"
    output_files = []

    if format in ['sqlite3', 'all']:
        sqlite_file = f"{base_filename}.db"
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        # Crea la tabella se non esiste
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lego_sets (
                lego_code TEXT PRIMARY KEY,
                official_name TEXT,
                number_of_pieces TEXT,
                number_of_minifigs TEXT,
                released TEXT,
                retired TEXT,
                retail_price_eur TEXT,
                retail_price_gbp TEXT,
                value_new_sealed TEXT,
                value_used TEXT,
                image_url TEXT,
                image_path TEXT,
                theme TEXT,
                subtheme TEXT,
                has_image INTEGER,
                pieces_numeric INTEGER
            )
        """)
        # Inserisci solo i nuovi set (evita duplicati)
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO lego_sets (
                    lego_code, official_name, number_of_pieces, number_of_minifigs, released, retired,
                    retail_price_eur, retail_price_gbp, value_new_sealed, value_used, image_url, image_path,
                    theme, subtheme, has_image, pieces_numeric
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['lego_code'], row['official_name'], row['number_of_pieces'], row['number_of_minifigs'],
                row['released'], row['retired'], row['retail_price_eur'], row['retail_price_gbp'],
                row['value_new_sealed'], row['value_used'], row['image_url'], row['image_path'],
                row['theme'], row['subtheme'], int(row['has_image']), row['pieces_numeric']
            ))
        conn.commit()
        output_files.append(sqlite_file)
        print(f"📦 SQLite database: {sqlite_file}")
    
    if format in ['html', 'all']:
        html_file = f"{base_filename}.html"
        df = pd.read_sql_query("SELECT * FROM lego_sets", conn)
        create_html_report(df, html_file)
        print(f"🌐 HTML rigenerato da SQLite: {html_file}")
        output_files.append(html_file)
        print(f"🌐 HTML report: {html_file}")
    
    conn.close()

    
    return output_files

def create_html_report(df: pd.DataFrame, filename: str):
    """Create HTML report with images"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LEGO Database Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .back-btn {
                display: inline-block;
                margin-bottom: 18px;
                padding: 10px 22px;
                font-size: 16px;
                border-radius: 8px;
                border: none;
                background: #764ba2;
                color: white;
                text-decoration: none;
                box-shadow: 0 2px 8px rgba(52,152,219,0.08);
                transition: background 0.2s;
            }
            .back-btn:hover {
                background: #667eea;
            }
            /* ...resto del CSS... */
        </style>
    </head>
    <body>
        <a href="index.html" class="back-btn">⬅️ Back to Main Page</a>
        <div class="container">
        
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
            image_src = f"images/{image_filename}"
            image_tag = f'<img src="{image_src}" class="set-image" alt="LEGO {row["lego_code"]}">'
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

def get_existing_lego_codes(sqlite_file="lego_database/LegoDatabase.db"):
    """Restituisce l'elenco dei lego_code già presenti nel database"""
    if not os.path.exists(sqlite_file):
        return set()
    conn = sqlite3.connect(sqlite_file)
    try:
        df = pd.read_sql_query("SELECT lego_code FROM lego_sets", conn)
        return set(df['lego_code'].tolist())
    except Exception:
        return set()
    finally:
        conn.close() 

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