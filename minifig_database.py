# --- Fixed version of minifig scraper ---
import os
import requests
import time
import pandas as pd
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import sqlite3

class MinifigImageDatabase:
    def __init__(self):
        self.images_dir = "lego_database/images"
        os.makedirs(self.images_dir, exist_ok=True)

    def download_image(self, minifig_code, image_url):
        if not image_url:
            return ''
        path = os.path.join(self.images_dir, f"{minifig_code}.jpg")
        if os.path.exists(path):
            return path
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            r = requests.get(image_url, timeout=10, headers=headers)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content)).convert('RGB')
            img.thumbnail((400, 400))
            img.save(path, format='JPEG', quality=90)
            return path
        except Exception as e:
            print(f"⚠️ Errore download immagine {minifig_code}: {e}")
            return ''

class EnhancedMinifigScraper:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)
        self.img_db = MinifigImageDatabase()

    def close(self):
        self.driver.quit()

    def safe_find_element(self, by, value, default=''):
        """Safely find element and return text or default value"""
        try:
            element = self.driver.find_element(by, value)
            return element.text.strip()
        except (NoSuchElementException, TimeoutException):
            return default

    def safe_find_elements(self, by, value):
        """Safely find elements and return list"""
        try:
            return self.driver.find_elements(by, value)
        except (NoSuchElementException, TimeoutException):
            return []

    def extract_minifig_data(self, minifig_code):
        data = {
            'minifig_code': minifig_code,
            'official_name': '',
            'theme': '',
            'year': '',
            'released': '',
            'retail_price_gbp': '',
            'has_image': False,
            'image_path': '',
            'sets': []  # <--- aggiunto campo sets
        }
        
        url = f"https://www.brickeconomy.com/minifig/{minifig_code}"
        print(f"   📡 Accessing: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Check if page exists by looking for title
            page_title = self.driver.title
            if "404" in page_title or "not found" in page_title.lower():
                print(f"   ❌ Page not found for {minifig_code}")
                data['official_name'] = 'Not found'
                return data

            # Extract name from page title or h1
            try:
                # Try multiple selectors for the name
                name_selectors = [
                    "h1",
                    ".minifig-title",
                    "[data-testid='minifig-name']",
                    ".page-title",
                    "title"
                ]
                
                name = ""
                for selector in name_selectors:
                    try:
                        if selector == "title":
                            name = self.driver.title
                        else:
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            name = element.text.strip()
                        if name and name != "BrickEconomy":
                            break
                    except:
                        continue
                
                # Clean up the name
                if name:
                    # Remove common suffixes
                    name = re.sub(r'\s*\|\s*BrickEconomy.*', '', name)
                    name = re.sub(r'\s*Minifigure\s*', '', name)
                    #name = re.sub(r'\s*LEGO\s*', '', name, flags=re.IGNORECASE)
                    name = name.strip()
                    data['official_name'] = name
                else:
                    data['official_name'] = 'Not found'
                    
            except Exception as e:
                print(f"   ⚠️ Error extracting name: {e}")
                data['official_name'] = 'Not found'

            # Try to extract additional info from page content
            try:
                page_source = self.driver.page_source
                
                # Look for theme information
                theme_patterns = [
                    r'Theme[:\s]*([^<\n\r]+)',
                    r'theme[:\s]*([^<\n\r]+)',
                    r'Series[:\s]*([^<\n\r]+)',
                ]
                
                for pattern in theme_patterns:
                    match = re.search(pattern, page_source, re.IGNORECASE)
                    if match:
                        theme = match.group(1).strip()
                        if len(theme) < 50:  # Reasonable theme name length
                            data['theme'] = theme
                            break

                
                # Look for year information
                rows = self.driver.find_elements(By.CSS_SELECTOR, ".row.rowlist")
                for row in rows:
                    cells = row.find_elements(By.CSS_SELECTOR, "div")
                    if len(cells) == 2:
                        label = cells[0].text.strip().lower()
                        value = cells[1].text.strip()
                        # Estrai l'anno
                        if label == "year" and re.match(r"\d{4}", value):
                            data['year'] = value
                        # Estrai la data di rilascio (mese e anno)
                        if label == "released" and value:
                            data['released'] = value
                        
                
                # Look for price information in USD first, then convert mentally to GBP
                rows = self.driver.find_elements(By.CSS_SELECTOR, ".row.rowlist")
                for row in rows:
                    cells = row.find_elements(By.CSS_SELECTOR, "div")
                    if len(cells) == 2:
                        label = cells[0].text.strip().lower()
                        value = cells[1].text.strip()
                        # Estrai prezzo se label contiene "value"
                        if "value" in label:
                            match = re.search(r"£\s?(\d+\.?\d*)", value)
                            if match:
                                data['retail_price_gbp'] = match.group(1)

            except Exception as e:
                print(f"   ⚠️ Error extracting details: {e}")

            # Try to find and download image
            try:
                # Look for images with various selectors
                image_selectors = [
                    "img[src*='minifig']",
                    "img[src*='lor001']",
                    f"img[src*='{minifig_code}']",
                    "img[alt*='minifig']",
                    "img[alt*='LEGO']",
                    ".minifig-image img",
                    ".product-image img",
                    "img"
                ]
                
                for selector in image_selectors:
                    try:
                        images = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for img in images:
                            src = img.get_attribute("src")
                            alt = img.get_attribute("alt") or ""
                            
                            if src and (
                                "minifig" in src.lower() or 
                                minifig_code.lower() in src.lower() or
                                "minifig" in alt.lower() or
                                (src.endswith(('.jpg', '.jpeg', '.png', '.webp')) and 
                                 not any(skip in src.lower() for skip in ['logo', 'icon', 'banner', 'header']))
                            ):
                                print(f"   🖼️ Found image: {src}")
                                path = self.img_db.download_image(minifig_code, src)
                                if path:
                                    data['image_path'] = path
                                    data['has_image'] = True
                                    break
                        
                        if data['has_image']:
                            break
                            
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"   ⚠️ Error extracting image: {e}")

            # Estrai i set che contengono la minifig
            try:
                sets = []
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.ctlsets-table")))
                tables = self.driver.find_elements(By.CSS_SELECTOR, "table.ctlsets-table")
                print(f"   📋 Found {len(tables)} tables")
                for table in tables:
                    h4_tags = table.find_elements(By.CSS_SELECTOR, "h4")
                    print(f"   📋 Found {len(h4_tags)} h4 tags in table")
                    for h4 in h4_tags:
                        links = h4.find_elements(By.CSS_SELECTOR, "a[href^='/set/']")
                        for link in links:
                            set_title = link.get_attribute("innerText").strip()
                            print(f"   📋 set title: '{set_title}'")
                            if set_title:
                                sets.append(set_title)
                data['sets'] = sets
                print(f"   📦 Sets found: {sets}")
            except Exception as e:
                print(f"   ⚠️ Error extracting sets: {e}")
                data['sets'] = []

            # Print what we found
            print(f"   ✅ Name: {data['official_name']}")
            print(f"   🎨 Theme: {data['theme'] or 'N/A'}")
            print(f"   📅 Year: {data['year'] or 'N/A'}")
            print(f"   📅 Released: {data['released'] or 'N/A'}")
            print(f"   💰 Price: {data['retail_price_gbp'] or 'N/A'}")
            print(f"   🖼️ Image: {'Yes' if data['has_image'] else 'No'}")
            print(f"   📦 Sets: {', '.join(data['sets']) if data['sets'] else 'N/A'}")

        except Exception as e:
            print(f"   ❌ Error accessing page for {minifig_code}: {e}")
            data['official_name'] = 'Error'

        return data

def debug_dataframe(df):
    """Debug function to check DataFrame content"""
    print("\n🔍 DEBUG: DataFrame Content")
    print("=" * 50)
    for idx, row in df.iterrows():
        print(f"Row {idx}: {row['minifig_code']}")
        print(f"  official_name: '{row['official_name']}'")
        print(f"  has_image: {row['has_image']}")
        print(f"  image_path: '{row['image_path']}'")
        if row['image_path']:
            print(f"  path exists: {os.path.exists(row['image_path'])}")
            if os.path.exists(row['image_path']):
                print(f"  file size: {os.path.getsize(row['image_path'])} bytes")
        print()

def create_minifig_database(minifig_codes, headless=True):
    scraper = EnhancedMinifigScraper(headless=headless)
    all_data = []
    
    for i, code in enumerate(minifig_codes, 1):
        print(f"\n🔎 {i}/{len(minifig_codes)}: Processing {code}")
        data = scraper.extract_minifig_data(code)
        all_data.append(data)
        
        # Add a small delay between requests to be respectful
        if i < len(minifig_codes):
            time.sleep(2)
    
    scraper.close()
    df = pd.DataFrame(all_data)
    return df

def export_minifig_database(df, format='all'):

    """Export database in multiple formats, always overwriting MinifigDatabase files"""
    base_filename = f"lego_database/LegoDatabase"
    output_files = []

    if format in ['sqlite3', 'all']:
        sqlite_file = f"{base_filename}.db"
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        # Crea la tabella se non esiste
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS minifig (
                minifig_code TEXT PRIMARY KEY,
                official_name TEXT,
                year TEXT,
                released TEXT,
                retail_price_gbp TEXT,
                has_image INTEGER,
                image_path TEXT,
                sets TEXT
            )
        """)
        # Inserisci solo i nuovi minifig (evita duplicati)
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO minifig (
                    minifig_code, official_name, year, released,
                    retail_price_gbp, has_image, image_path, sets
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['minifig_code'],
                row['official_name'],
                row['year'],
                row['released'],
                row['retail_price_gbp'],
                int(row['has_image']),
                row['image_path'],
                ', '.join(row['sets']) if isinstance(row['sets'], list) else row['sets']
            ))
        conn.commit()
        
        output_files.append(sqlite_file)
        print(f"📦 SQLite database: {sqlite_file}")

    if format in ['html', 'all']:
        html_file = f"{base_filename}.html"
        df = pd.read_sql_query("SELECT * FROM minifig", conn)
        create_minifig_html_report(df, html_file)
        print(f"🌐 HTML rigenerato da SQLite: {html_file}")
        create_minifig_html_report(df, html_file)
        output_files.append(html_file)
        print(f"🌐 HTML report: {html_file}")

    conn.close()

    return output_files

def create_minifig_html_report(df: pd.DataFrame, filename: str):
    import shutil
    html_dir = os.path.dirname(filename)
    if not html_dir:  # If filename has no directory
        html_dir = os.getcwd()
    images_dir = os.path.join(html_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    print(f"📁 HTML report directory: {html_dir}")
    print(f"🖼️ Images directory: {images_dir}")
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LEGO Minifigure Database Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .minifig-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; display: flex; align-items: center; background: #f9f9f9; transition: transform 0.2s; }
            .minifig-card:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            .minifig-image { width: 150px; height: 150px; object-fit: contain; margin-right: 20px; border: 1px solid #ccc; background: white; border-radius: 5px; }
            .minifig-info { flex: 1; }
            .minifig-title { font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
            .minifig-details { margin: 5px 0; color: #666; }
            .minifig-code { background: #3498db; color: white; padding: 2px 8px; border-radius: 4px; font-family: monospace; font-size: 12px; }
            .not-found { opacity: 0.6; background: #ffeaa7; }
            .error { opacity: 0.6; background: #fab1a0; }
            .summary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .summary h2 { margin-top: 0; }
            .stats { display: flex; justify-content: space-around; margin: 15px 0; }
            .stat { text-align: center; }
            .stat-number { font-size: 24px; font-weight: bold; }
            .stat-label { font-size: 14px; opacity: 0.9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧱 LEGO Minifigure Database Report</h1>
    """
    
    total = len(df)
    found = len(df[(df['official_name'].notna()) & (df['official_name'] != 'Not found') & (df['official_name'] != 'Error')])
    with_images = len(df[df['has_image'] == True])
    errors = len(df[df['official_name'] == 'Error'])
    
    html_content += f"""
            <div class="summary">
                <h2>📊 Database Summary</h2>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{total}</div>
                        <div class="stat-label">Total Processed</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{found}</div>
                        <div class="stat-label">Successfully Found</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{with_images}</div>
                        <div class="stat-label">With Images</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{100*found/total:.1f}%</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                </div>
            </div>
            <h2>🧑‍🚀 Minifigure Details</h2>
    """
    
    for _, row in df.iterrows():
        is_found = row['official_name'] not in ['Not found', 'Error', ''] and pd.notna(row['official_name'])
        is_error = row['official_name'] == 'Error'
        
        if is_error:
            card_class = "minifig-card error"
        elif not is_found:
            card_class = "minifig-card not-found"
        else:
            card_class = "minifig-card"
        
        print(f"\n🔍 Processing HTML for {row['minifig_code']}:")
        print(f"   has_image: {row['has_image']}")
        print(f"   image_path: '{row['image_path']}'")
        
        # Handle image
        image_tag = ""
        if row['has_image'] and pd.notna(row['image_path']) and row['image_path'] and os.path.exists(str(row['image_path'])):
            print(f"   ✅ Source image exists: {row['image_path']}")
            image_filename = f"{row['minifig_code']}.jpg"
            dest_path = os.path.join(images_dir, image_filename)
            
            try:
                # Ensure source path is absolute
                #source_path = os.path.abspath(str(row['image_path']))
                dest_path = os.path.abspath(dest_path)
                
                #print(f"   📋 Copying: {source_path}")
                print(f"   📋 To: {dest_path}")
                
                # Copy image to HTML directory
                #shutil.copy2(source_path, dest_path)
                print(f"   ✅ Copy successful")
                
                # Verify the copied file exists
                if os.path.exists(dest_path):
                    file_size = os.path.getsize(dest_path)
                    print(f"   ✅ Destination file exists, size: {file_size} bytes")
                    image_src = f"images/{image_filename}"
                    image_tag = f'<img src="{image_src}" class="minifig-image" alt="LEGO {row["minifig_code"]}">' 
                else:
                    print(f"   ❌ Destination file doesn't exist after copy")
                    image_tag = '<div class="minifig-image" style="display:flex;align-items:center;justify-content:center;color:#999;font-size:12px;">Copy Failed</div>'
                    
            except Exception as e:
                print(f"   ❌ Error copying image: {e}")
                print(f"   📋 Exception type: {type(e).__name__}")
                image_tag = f'<div class="minifig-image" style="display:flex;align-items:center;justify-content:center;color:#999;font-size:12px;">Copy Error: {type(e).__name__}</div>'
        else:
            # Debug info for missing images
            print(f"   ❌ Image not available:")
            if not row['has_image']:
                print(f"      - has_image is False")
            if not pd.notna(row['image_path']) or not row['image_path']:
                print(f"      - image_path is empty or NaN")
            elif not os.path.exists(str(row['image_path'])):
                print(f"      - image_path doesn't exist: {row['image_path']}")
            image_tag = '<div class="minifig-image" style="display:flex;align-items:center;justify-content:center;color:#999;font-size:12px;">No Image</div>'
        
        # Handle name and details
        if is_error:
            name = f"❌ Error loading {row['minifig_code']}"
        elif not is_found:
            name = f"❓ {row['minifig_code']} (Not Found)"
        else:
            name = row['official_name']
        
        year = f"📅 {row['year']}" if pd.notna(row['year']) and row['year'] else ""
        price = f"💰 £{row['retail_price_gbp']}" if pd.notna(row['retail_price_gbp']) and row['retail_price_gbp'] else ""
        
        html_content += f"""
            <div class="{card_class}">
                {image_tag}
                <div class="minifig-info">
                    <div class="minifig-title">
                        <span class="minifig-code">{row['minifig_code']}</span>
                        {name}
                    </div>
                    <div class="minifig-details">{year}</div>
                    <div class="minifig-details">{price}</div>
                    <div class="minifig-details">📅 Released: {row['released'] if pd.notna(row['released']) and row['released'] else 'N/A'}</div>
                    <div class="minifig-details">
                        <b>📦 Sets:</b>
                        {('<ul style="margin:4px 0 0 18px;">' + ''.join(f'<li>{s}</li>' for s in row['sets']) + '</ul>') if isinstance(row['sets'], list) and row['sets'] else 'N/A'}
                    </div>
                </div>
            </div>
        """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    import sys
    print("🏗️ ENHANCED MINIFIG DATABASE CREATOR")
    print("Creates comprehensive minifig database with images")
    print("=" * 50)

    # Codici ad-hoc (aggiungi qui quelli che vuoi in futuro)
    extra_codes = [
        "dim001", "dim007", "dim008"
        # aggiungi altri codici qui
    ]

    # Range automatico lor001-lor153
    auto_codes = [f"lor{str(i).zfill(3)}" for i in range(1, 154) if i != 108] # Skip lor108 as it's not a minifig

    # Se passi codici da terminale, usali; altrimenti usa auto + extra
    if len(sys.argv) > 1:
        codes = [c.strip() for c in sys.argv[1].split(',')]
    else:
        codes = auto_codes + extra_codes
        print(f"Using codes: {', '.join(codes)}")

    print(f"\n🏗️ CREATING MINIFIG DATABASE")
    print(f"🧑‍🚀 Processing {len(codes)} minifigs with enhanced scraping")
    print("=" * 60)

    start_time = time.time()
    df = create_minifig_database(codes, headless=True)
    
    # Debug the DataFrame to see what we actually got
    debug_dataframe(df)
    
    print(f"\n📊 EXPORTING DATABASE")
    files = export_minifig_database(df, format='all')

    elapsed = time.time() - start_time
    found = len(df[(df['official_name'].notna()) & (df['official_name'] != 'Not found') & (df['official_name'] != 'Error')])
    with_images = len(df[df['has_image'] == True])

    print("\n" + "=" * 60)
    print(f"🎯 DATABASE CREATED in {elapsed:.1f} seconds")
    print(f"📊 Success: {found}/{len(codes)} minifigs ({100*found/len(codes):.1f}%)")
    print(f"🖼️ Images: {with_images}/{len(codes)} downloaded ({100*with_images/len(codes):.1f}%)")

    print("\n🎉 Database created successfully!")
    print("📁 Files generated:")
    for f in files:
        print(f"   📄 {f}")
    
    print("\n💡 Tip: Open the HTML file to view your minifig database with images!")
    print("🔧 If success rate is low, try running with headless=False for debugging")

if __name__ == "__main__":
    main()