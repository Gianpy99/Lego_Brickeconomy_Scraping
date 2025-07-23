"""
Debug scraper per identificare il problema con i selettori
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

def debug_brickeconomy_search(lego_code="75192"):
    """Debug della ricerca su BrickEconomy"""
    
    options = Options()
    # NON usare headless per il debug
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    
    try:
        print(f"🔍 Testing search for LEGO code: {lego_code}")
        
        # 1. Vai al sito
        driver.get("https://www.brickeconomy.com/")
        print("✅ Sito caricato")
        
        # Aspetta che la pagina si carichi completamente
        time.sleep(5)
        
        # 2. Gestisci TUTTI i possibili popup aggressivamente
        popup_selectors = [
            '//*[@id="ez-accept-all"]',
            '//button[contains(text(), "Accept")]',
            '//button[contains(text(), "OK")]',
            '//button[contains(text(), "Close")]',
            '//*[@class="close"]',
            '//*[contains(@class, "modal")]//button',
        ]
        
        for selector in popup_selectors:
            try:
                popup = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                popup.click()
                print(f"✅ Popup chiuso: {selector}")
                time.sleep(1)
            except:
                continue
        
        # Usa JavaScript per rimuovere overlay nascosti
        driver.execute_script("""
            // Rimuovi overlay e modal nascosti
            var overlays = document.querySelectorAll('[style*="z-index"], .modal, .popup, [class*="overlay"]');
            overlays.forEach(function(el) { el.remove(); });
            
            // Forza visibilità del campo di ricerca
            var searchBox = document.getElementById('txtSearchHeader');
            if (searchBox) {
                searchBox.style.visibility = 'visible';
                searchBox.style.display = 'block';
                searchBox.disabled = false;
            }
        """)
        
        print("✅ Cleanup popup completato")
        
        # 3. Trova campo di ricerca e aspetta che sia interagibile
        search_box = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="txtSearchHeader"]'))
        )
        
        # Scroll fino al campo di ricerca
        driver.execute_script("arguments[0].scrollIntoView(true);", search_box)
        time.sleep(1)
        
        # Clicca prima per assicurarsi che sia attivo
        search_box.click()
        time.sleep(0.5)
        
        # Pulisci e inserisci il codice
        search_box.clear()
        search_box.send_keys(lego_code)
        search_box.send_keys(Keys.RETURN)
        print(f"✅ Ricerca iniziata per: {lego_code}")
        
        # 4. Click su tab Sets
        sets_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="#sets"]'))
        )
        sets_tab.click()
        print("✅ Tab Sets cliccato")
        
        # 5. Aspetta che i risultati si carichino
        time.sleep(3)
        
        # 6. Debug: trova tutti i possibili risultati
        print("\n🔍 ANALISI RISULTATI:")
        
        # Controlla se ci sono risultati
        try:
            results_table = driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]')
            print("✅ Tabella risultati trovata")
            
            # Trova tutte le righe
            rows = driver.find_elements(By.XPATH, '//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]//tr')
            print(f"📊 Trovate {len(rows)} righe nella tabella")
            
            # Analizza le prime righe (salta header)
            for i, row in enumerate(rows[1:6], 1):  # Prendi prime 5 righe dopo header
                try:
                    # Cerca link del set
                    set_links = row.find_elements(By.XPATH, './/a[contains(@href, "set")]')
                    if set_links:
                        set_name = set_links[0].text.strip()
                        set_href = set_links[0].get_attribute('href')
                        print(f"  📦 Riga {i}: '{set_name}' -> {set_href}")
                        
                        # Prova diversi selettori per questo link
                        selectors_to_test = [
                            f'//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]//tr[{i+1}]//a[contains(@href, "set")]',
                            f'//tr[{i+1}]//h4//a',
                            f'//a[contains(@href, "set") and contains(text(), "{set_name[:10]}")]'
                        ]
                        
                        for j, selector in enumerate(selectors_to_test):
                            try:
                                test_element = driver.find_element(By.XPATH, selector)
                                if test_element and test_element.is_displayed():
                                    print(f"    ✅ Selettore {j+1} funziona: {selector}")
                                else:
                                    print(f"    ❌ Selettore {j+1} trovato ma non visibile")
                            except:
                                print(f"    ❌ Selettore {j+1} non funziona")
                    else:
                        print(f"  ❌ Riga {i}: Nessun link trovato")
                        
                except Exception as e:
                    print(f"  ❌ Errore riga {i}: {str(e)}")
            
            # Test click sul primo risultato valido
            print(f"\n🎯 TENTATIVO CLICK SUL PRIMO RISULTATO:")
            first_result_selectors = [
                '//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]//tr[2]//a[contains(@href, "set")]',
                '//tr[2]//h4//a[contains(@href, "set")]',
                '//*[@id="ContentPlaceHolder1_ctlSets_GridViewSets"]//a[contains(@href, "set")]'
            ]
            
            clicked = False
            for i, selector in enumerate(first_result_selectors, 1):
                try:
                    element = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    set_name = element.text.strip()
                    print(f"✅ Selettore {i} trovato: '{set_name}'")
                    
                    # Prova a cliccare
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    element.click()
                    
                    print(f"✅ CLICK RIUSCITO con selettore {i}!")
                    clicked = True
                    
                    # Aspetta che la pagina si carichi
                    time.sleep(3)
                    
                    # Verifica che siamo nella pagina del set
                    current_url = driver.current_url
                    if "set" in current_url:
                        print(f"✅ Navigazione riuscita: {current_url}")
                        
                        # Cerca informazioni base
                        try:
                            name_element = driver.find_element(By.XPATH, '//h1')
                            print(f"📦 Nome del set: {name_element.text}")
                        except:
                            print("⚠️ Nome del set non trovato")
                            
                        try:
                            pieces_element = driver.find_element(By.XPATH, '//*[contains(text(), "Pieces")]/following-sibling::*[1]')
                            print(f"🧩 Pezzi: {pieces_element.text}")
                        except:
                            print("⚠️ Numero pezzi non trovato")
                            
                    else:
                        print(f"⚠️ Navigazione non riuscita, URL: {current_url}")
                    
                    break
                    
                except Exception as e:
                    print(f"❌ Selettore {i} fallito: {str(e)}")
            
            if not clicked:
                print("❌ NESSUN CLICK RIUSCITO!")
                
        except Exception as e:
            print(f"❌ Errore nella tabella risultati: {str(e)}")
        
        print("\n⏱️ Pausa per ispezione manuale (30 secondi)...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Errore generale: {str(e)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_brickeconomy_search("75192")  # UCS Millennium Falcon
