import os
import json
import subprocess
import sys
from playwright.sync_api import sync_playwright

def install_playwright_browsers():
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
    except Exception as e:
        print(f"Note installation : {e}")

def run_scraper():
    install_playwright_browsers()
    print("Démarrage du scraper et consolidation locale...")

    # 1. Récupération des données automatisées (là où les robots l'autorisent)
    donnees_auto = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # --- Insère ici tes actions de scraping automatique ---
        # page.goto("URL_autorisee")
        # donnees_auto["site_xyz"] = page.inner_text("...")
        
        browser.close()

    # Simulation de données automatiques pour l'exemple
    donnees_auto["statut_auto"] = "Récupéré avec succès via Playwright"

    # 2. Lecture de ton fichier de saisie manuelle présent dans le dépôt scrapeur
    chemin_manuel = "tarifs_manuels.json"
    donnees_manuelles = {}
    
    if os.path.exists(chemin_manuel):
        with open(chemin_manuel, "r", encoding="utf-8") as f:
            donnees_manuelles = json.load(f)
        print("Fichier 'tarifs_manuels.json' chargé avec succès.")
    else:
        print("Attention : 'tarifs_manuels.json' introuvable dans le dépôt.")

    # 3. Fusion des deux mondes dans un dictionnaire global unique
    grille_complete = {
        "metadonnees": {
            "derniere_maj": "2026-11-01",
            "mode": "Hybride (Auto + Manuel)"
        },
        "donnees_automatiques": donnees_auto,
        "donnees_manuelles_et_confirmees": donnees_manuelles
    }

    # 4. Enregistrement dans un NOUVEAU fichier local (ex: grille_consolidee.json)
    # Ce fichier reste sagement dans ton dépôt scrapeur sans toucher à ton site
    nom_fichier_sortie = "grille_consolidee.json"
    with open(nom_fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(grille_complete, f, indent=2, ensure_ascii=False)
    
    print(f"Fichier consolidé '{nom_fichier_sortie}' généré avec succès dans 'scrapeur' !")

if __name__ == "__main__":
    run_scraper()
