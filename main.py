import sys

# Importa le funzioni principali dai tuoi moduli
from lego_database import main as lego_main
from minifig_database import main as minifig_main
def create_landing_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LEGO Database Landing Page</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; }
            .container { max-width: 600px; margin: 60px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
            h1 { color: #2c3e50; margin-bottom: 30px; }
            .btn { display: inline-block; margin: 20px 10px; padding: 18px 32px; font-size: 18px; border-radius: 8px; border: none; background: #3498db; color: white; text-decoration: none; box-shadow: 0 2px 8px rgba(52,152,219,0.1); transition: background 0.2s; }
            .btn:hover { background: #217dbb; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧱 LEGO Database</h1>
            <a href="LegoDatabase.html" class="btn">📦 Vai ai Set LEGO del signore degli anelli</a>
            <a href="LegoDatabase_Minifig.html" class="btn">🧑‍🚀 Vai alle Minifig LEGO del signore degli anelli</a>
        </div>
    </body>
    </html>
    """
    with open("lego_database/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Landing page creata: lego_database/index.html")

def main():
    print("🧱 LEGO DATABASE PROJECT")
    print("=" * 40)
    print("1. Genera database dei set LEGO")
    print("2. Genera database delle minifig")
    print("3. Genera entrambi")
    print("4. Crea landing page HTML")
    print("0. Esci")
    scelta = input("Scegli un'opzione: ").strip()

    if scelta == "1":
        print("\n--- DATABASE SET LEGO ---")
        lego_main()
    elif scelta == "2":
        print("\n--- DATABASE MINIFIG ---")
        minifig_main()
    elif scelta == "3":
        print("\n--- DATABASE SET LEGO ---")
        lego_main()
        print("\n--- DATABASE MINIFIG ---")
        minifig_main()
    elif scelta == "4":
        create_landing_page()
    else:
        print("Uscita.")

if __name__ == "__main__":
    main()