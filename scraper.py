import os
import json
import subprocess
import sys
from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def install_playwright_browsers():
    """S'assure que les navigateurs Playwright sont disponibles."""
    print("Vérification des navigateurs Playwright...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
    except Exception as e:
        print(f"Note installation : {e}")

def scraper_donnees_ouvertes():
    """
    Explore les sites accessibles (qui ne bloquent pas par WAF/robots.txt)
    pour récupérer un maximum de données en automatique.
    """
    donnees_auto = {}
    print("Lancement du scraping automatique des sources ouvertes...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # --- EXEMPLE DE SCRAPING CIBLÉ (Fournisseurs alternatifs ouverts) ---
        try:
            # Exemple : Visiter un fournisseur ou un comparateur accessible
            # page.goto("https://www.fournisseur-alternatif-ouvert.fr", timeout=30000)
            # prix = page.locator(".selecteur-prix").inner_text()
            # donnees_auto["fournisseur_alternatif"] = {"prix_kwh": prix}
            pass
        except Exception as e:
            print(f"Erreur sur une source ouverte : {e}")

        browser.close()
        
    return donnees_auto

def run_consolidation():
    install_playwright_browsers()
    print("=== Démarrage de la consolidation globale ===" )

    # 1. Récupération des données automatisées possibles
    donnees_auto = scraper_donnees_ouvertes()

    # 2. Chargement de ton fichier de saisie manuelle (EDF, Engie, ilek, etc.)
    chemin_manuel = "tarifs_manuels.json"
    donnees_manuelles = {}
    
    if os.path.exists(chemin_manuel):
        with open(chemin_manuel, "r", encoding="utf-8") as f:
            donnees_manuelles = json.load(f)
        print("Succès : Fichier 'tarifs_manuels.json' chargé (filet de sécurité manuel).")
    else:
        print("Attention : 'tarifs_manuels.json' introuvable.")

    # 3. Fusion intelligente : Le manuel complète ou remplace l'automatique si bloqué
    grille_globale = {
        "metadonnees": {
            "derniere_mise_a_jour": "2026-11-01",
            "statut": "Généré automatiquement par le dépôt scrapeur sur Render"
        },
        "donnees_collectees_automatiquement": donnees_auto,
        "donnees_saisies_manuellement_et_confirmees": donnees_manuelles
    }

    # 4. Enregistrement dans le fichier consolidé local
    fichier_sortie = "grille_consolidee.json"
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(grille_globale, f, indent=2, ensure_ascii=False)
        
    print(f"Fichier global '{fichier_sortie}' mis à jour avec succès !")

@app.route("/")
def home():
    run_consolidation()
    return "Scraping et consolidation exécutés avec succès !"

if __name__ == "__main__":
    try:
        run_consolidation()
    except Exception as e:
        print(f"Erreur au démarrage : {e}")
        
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
