"""
Debug delle immagini su BrickEconomy per capire la struttura
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def debug_images_on_brickeconomy(lego_code="75192"):
    """Debug delle immagini per un set specifico"""
    
    options = Options()
    options.add_argument("--headless")  # Headless per velocità
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print(f"🖼️ DEBUGGING IMAGES FOR: {lego_code}")
        
        # 1. Vai al sito
        driver.get("https://www.brickeconomy.com/")
        print("✅ Sito caricato")
        
        # 2. Gestisci popup cookie aggressivamente 
        time.sleep(2)
        driver.execute_script("""
            var acceptBtns = document.querySelectorAll('button[id*="accept"], button[class*="accept"], [data-testid*="accept"], button[id="ez-accept-all"]');
            acceptBtns.forEach(function(btn) { 
                if(btn.offsetParent && btn.style.display !== 'none') {
                    btn.click(); 
                }
            });
        """)
        
        # 3. Cerca il set
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="txtSearchHeader"]'))
        )
        search_box.clear()
        search_box.send_keys(lego_code)
        search_box.send_keys(Keys.RETURN)
        print(f"✅ Ricerca per {lego_code}")
        
        # 4. Click tab Sets
        sets_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="#sets"]'))
        )
        sets_tab.click()
        time.sleep(2)
        
        # 5. Click primo risultato
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]//tr[2]//a[contains(@href, "set")]'))
        )
        first_result.click()
        print("✅ Navigato alla pagina del set")
        
        # 6. Aspetta il caricamento della pagina
        time.sleep(3)
        
        # 7. DEBUG - Trova TUTTE le immagini
        print("\n🔍 ANALISI IMMAGINI PRESENTI:")
        
        # Trova tutte le immagini
        all_images = driver.find_elements(By.TAG_NAME, "img")
        print(f"📊 Trovate {len(all_images)} immagini totali")
        
        # Analizza ogni immagine
        valid_images = []
        for i, img in enumerate(all_images):
            try:
                src = img.get_attribute('src')
                alt = img.get_attribute('alt') or ''
                width = img.get_attribute('width') or '0'
                height = img.get_attribute('height') or '0'
                
                if src:
                    print(f"\n📷 Immagine {i+1}:")
                    print(f"   SRC: {src}")
                    print(f"   ALT: {alt}")
                    print(f"   SIZE: {width}x{height}")
                    
                    # Criteri per immagine valida del set
                    is_valid = (
                        'http' in src and 
                        ('.jpg' in src.lower() or '.png' in src.lower()) and
                        (lego_code in src or 'set' in src.lower() or 'lego' in alt.lower()) and
                        not any(skip in src.lower() for skip in ['icon', 'logo', 'button', 'banner'])
                    )
                    
                    if is_valid:
                        try:
                            w = int(width) if width.isdigit() else 0
                            h = int(height) if height.isdigit() else 0
                            if w > 100 and h > 100:  # Immagine abbastanza grande
                                valid_images.append({
                                    'src': src,
                                    'alt': alt,
                                    'width': w,
                                    'height': h
                                })
                                print(f"   ✅ VALIDA per il set!")
                        except:
                            pass
                    
            except Exception as e:
                print(f"   ❌ Errore nell'analisi: {str(e)}")
        
        print(f"\n🎯 RISULTATO FINALE:")
        print(f"📊 Immagini valide trovate: {len(valid_images)}")
        
        if valid_images:
            print("\n🏆 MIGLIORI CANDIDATI:")
            # Ordina per dimensione (più grande = migliore)
            valid_images.sort(key=lambda x: x['width'] * x['height'], reverse=True)
            
            for i, img in enumerate(valid_images[:3], 1):  # Top 3
                print(f"   {i}. {img['src']}")
                print(f"      Alt: {img['alt']}")
                print(f"      Size: {img['width']}x{img['height']}")
                print()
        else:
            print("❌ Nessuna immagine valida trovata")
            
            # DEBUG AGGIUNTIVO: Cerca pattern alternativi
            print("\n🔍 DEBUG AGGIUNTIVO - Pattern alternativi:")
            
            # Cerca in div specifici
            set_divs = driver.find_elements(By.XPATH, "//*[contains(@class, 'set') or contains(@id, 'set')]")
            print(f"   Div con 'set': {len(set_divs)}")
            
            # Cerca immagini con pattern BrickEconomy
            be_images = driver.find_elements(By.XPATH, "//img[contains(@src, 'brickeconomy') or contains(@src, 'lego')]")
            print(f"   Immagini BrickEconomy/LEGO: {len(be_images)}")
            
            for img in be_images[:5]:  # Prime 5
                src = img.get_attribute('src')
                print(f"     - {src}")
        
        return valid_images[0]['src'] if valid_images else None
        
    except Exception as e:
        print(f"❌ Errore generale: {str(e)}")
        return None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    # Test con set popolare
    image_url = debug_images_on_brickeconomy("75192")
    if image_url:
        print(f"\n✅ URL IMMAGINE TROVATA: {image_url}")
    else:
        print(f"\n❌ NESSUNA IMMAGINE TROVATA")
