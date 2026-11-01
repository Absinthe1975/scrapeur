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
    print("Démarrage du scraping et fusion des données...")

    # 1. Données récupérées automatiquement (là où c'est autorisé/accessible)
    donnees_auto = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Exemple de ce que tu arrives à lire automatiquement
        # ... ton code de scraping ici ...
        
        browser.close()

    # Données simulées automatiques pour l'exemple
    donnees_auto = {
        "source": "automatique",
        "date_maj": "2026-11-01",
        "fournisseurs_dispo": ["Alterna", "TotalEnergies (Offres éligibles)"]
    }

    # 2. Charger tes données manuelles / À confirmer (EDF, Engie, ilek, etc.)
    # Tu peux stocker un fichier "tarifs_manuels.json" directement dans ton dépôt scrapeur
    chemin_manuel = "tarifs_manuels.json"
    donnees_manuelles = {}
    if os.path.exists(chemin_manuel):
        with open(chemin_manuel, "r", encoding="utf-8") as f:
            donnees_manuelles = json.load(f)
    else:
        # Structure de secours si le fichier n'existe pas encore
        donnees_manuelles = {
            "source": "manuel_et_pdf",
            "statut": "En attente de saisie",
            "fournisseurs": {
                "EDF": {"statut": "À confirmer", "note": "Interdit robots.txt - Données grilles manuelles"},
                "ENGIE": {"statut": "À confirmer", "note": "Saisi à la main"},
                "ilek": {"statut": "À confirmer", "note": "Page non lisible par le script"}
            }
        }

    # 3. Fusionner le tout dans un unique fichier final propre
    grille_globale = {
        "metadonnees": {
            "derniere_generation": "2026-11-01"
        },
        "donnees_automatiques": donnees_auto,
        "donnees_manuelles_et_confirmees": donnees_manuelles
    }

    # 4. Enregistrer dans un nouveau fichier local : "grille_finale.json"
    nom_fichier_sortie = "grille_finale.json"
    with open(nom_fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(grille_globale, f, indent=2, ensure_ascii=False)
    
    print(f"Fichier '{nom_fichier_sortie}' généré avec succès dans le dépôt scrapeur !")

if __name__ == "__main__":
    run_scraper()
