import os
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image
from io import BytesIO
import shutil
import time

def create_minifig_database(minifig_codes, headless=True):
    """
    Crea un database di minifigure LEGO da BrickEconomy.
    Args:
        minifig_codes (list): Lista di codici minifigure (es: ['lor001'])
        headless (bool): Esegui Chrome in modalità headless
    Returns:
        pd.DataFrame: Database minifigure
    """
    results = []
    for code in minifig_codes:
        data = scrape_minifig(code, headless=headless)
        results.append(data)
    df = pd.DataFrame(results)
    return df

def scrape_minifig(minifig_code, headless=True):
    """Estrae dati e thumbnail per una minifigure BrickEconomy"""
    url = "https://www.brickeconomy.com/"
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)
    data = {
        'minifig_code': minifig_code,
        'official_name': 'Not found',
        'theme': '',
        'year': '',
        'has_image': False,
        'image_path': '',
        'retail_price_gbp': '',
    }
    try:
        driver.get(url)
        # Cerca la minifigure
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtSearchHeader"]')))
        search_box.clear()
        search_box.send_keys(minifig_code)
        search_box.send_keys(Keys.RETURN)
        # Clicca tab Minifigures
        minifig_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#minifigs"]')))
        minifig_tab.click()
        # Clicca primo risultato
        first_result = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_ctlMinifigs_GridViewMinifigs"]/tbody/tr[2]/td[2]/div[1]/h4/a')))
        first_result.click()
        # Estrai nome
        try:
            name_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_SetTitle"]')))
            data['official_name'] = name_elem.text.strip()
        except:
            pass
        # Estrai tema
        try:
            theme_elem = driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_SetTheme"]/a')
            data['theme'] = theme_elem.text.strip()
        except:
            pass
        # Estrai anno
        try:
            year_elem = driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_SetYear"]')
            data['year'] = year_elem.text.strip()
        except:
            pass
        # Estrai prezzo GBP
        try:
            price_elem = driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_PanelSetFacts"]/div[3]/div[3]/div[2]')
            data['retail_price_gbp'] = price_elem.text.strip()
        except:
            pass
        # Estrai thumbnail
        try:
            img_elem = driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_SetImage"]//img')
            img_url = img_elem.get_attribute('src')
            if img_url:
                img_path = download_minifig_image(minifig_code, img_url)
                data['image_path'] = img_path
                data['has_image'] = True
        except:
            pass
    except Exception as e:
        print(f"❌ {minifig_code}: {e}")
    finally:
        driver.quit()
    return data

def download_minifig_image(minifig_code, url):
    """Scarica e salva la thumbnail della minifigure"""
    images_dir = os.path.join('minifig_database', 'images')
    os.makedirs(images_dir, exist_ok=True)
    img_path = os.path.join(images_dir, f"{minifig_code}.jpg")
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert('RGB')
        img.thumbnail((400, 400))
        img.save(img_path, format='JPEG', quality=90)
        return img_path
    except Exception as e:
        print(f"❌ Errore download immagine {minifig_code}: {e}")
        return ''

def export_minifig_database(df, format='all'):
    """Esporta il database minifigure in vari formati"""
    base_filename = f"minifig_database/minifig_database_{int(time.time())}"
    os.makedirs('minifig_database', exist_ok=True)
    output_files = []
    if format in ['excel', 'all']:
        excel_file = f"{base_filename}.xlsx"
        df.to_excel(excel_file, index=False)
        output_files.append(excel_file)
    if format in ['csv', 'all']:
        csv_file = f"{base_filename}.csv"
        df.to_csv(csv_file, index=False)
        output_files.append(csv_file)
    if format in ['html', 'all']:
        html_file = f"{base_filename}.html"
        create_minifig_html_report(df, html_file)
        output_files.append(html_file)
    return output_files

def create_minifig_html_report(df: pd.DataFrame, filename: str):
    """Crea un report HTML con immagini per minifigure"""
    import shutil
    html_dir = os.path.dirname(filename)
    images_dir = os.path.join(html_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LEGO Minifigure Database Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .minifig-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; display: flex; align-items: center; background: #f9f9f9; }
            .minifig-image { width: 150px; height: 150px; object-fit: contain; margin-right: 20px; border: 1px solid #ccc; background: white; }
            .minifig-info { flex: 1; }
            .minifig-title { font-size: 18px; font-weight: bold; color: #2c3e50; }
            .minifig-details { margin: 5px 0; }
            .not-found { opacity: 0.5; }
            .summary { background: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>🧱 LEGO Minifigure Database Report</h1>
    """
    total = len(df)
    found = len(df[df['official_name'].notna() & (df['official_name'] != 'Not found')])
    with_images = len(df[df['has_image'] == True])
    html_content += f"""
        <div class=\"summary\">
            <h2>📊 Summary</h2>
            <p><strong>Total Minifigures:</strong> {total}</p>
            <p><strong>Successfully Found:</strong> {found} ({100*found/total:.1f}%)</p>
            <p><strong>With Images:</strong> {with_images} ({100*with_images/total:.1f}%)</p>
        </div>
        <h2>🧑‍🚀 Minifigures</h2>
    """
    for _, row in df.iterrows():
        is_found = row['official_name'] != 'Not found' and row['official_name']
        card_class = "minifig-card" if is_found else "minifig-card not-found"
        # Immagine
        if row['has_image'] and os.path.exists(row['image_path']):
            image_filename = f"{row['minifig_code']}.jpg"
            dest_path = os.path.join(images_dir, image_filename)
            try:
                shutil.copy2(row['image_path'], dest_path)
                image_src = f"images/{image_filename}"
                image_tag = f'<img src="{image_src}" class="minifig-image" alt="LEGO {row["minifig_code"]}">'
            except Exception as e:
                print(f"⚠️ Errore copia immagine {row['minifig_code']}: {e}")
                image_tag = '<div class="minifig-image" style="display:flex;align-items:center;justify-content:center;color:#999;">Image Error</div>'
        else:
            image_tag = '<div class="minifig-image" style="display:flex;align-items:center;justify-content:center;color:#999;">No Image</div>'
        # Info
        name = row['official_name'] if is_found else f"Minifig {row['minifig_code']} (Not Found)"
        theme = f"🎨 {row['theme']}" if row['theme'] else ""
        year = f"📅 {row['year']}" if row['year'] else ""
        price = f"💰 {row['retail_price_gbp']}" if row['retail_price_gbp'] else ""
        html_content += f"""
            <div class=\"{card_class}\">
                {image_tag}
                <div class=\"minifig-info\">
                    <div class=\"minifig-title\">{row['minifig_code']}: {name}</div>
                    <div class=\"minifig-details\">{theme}</div>
                    <div class=\"minifig-details\">{year}</div>
                    <div class=\"minifig-details\">{price}</div>
                </div>
            </div>
        """
    html_content += """
        </body>
    </html>
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

#Esempio d'uso (decommenta per test standalone)
if __name__ == "__main__":
    codes = ["lor001", "sw001"]
    df = create_minifig_database(codes, headless=True)
    files = export_minifig_database(df, format='all')
    print(files)
