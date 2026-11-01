import os
import json
import subprocess
import sys
from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def install_playwright_browsers():
    print("Vérification des navigateurs Playwright...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
    except Exception as e:
        print(f"Note installation : {e}")

def run_consolidation():
    install_playwright_browsers()
    print("=== Démarrage de la consolidation globale ===")

    # Chemin vers ton fichier manuel dans le dossier donnees
    chemin_manuel = os.path.join("donnees", "tarifs_manuels.json")
    donnees_manuelles = {}
    
    if os.path.exists(chemin_manuel):
        with open(chemin_manuel, "r", encoding="utf-8") as f:
            donnees_manuelles = json.load(f)
        print("Succès : Fichier 'tarifs_manuels.json' chargé.")
    else:
        print(f"Attention : Fichier introuvable à {chemin_manuel}")

    grille_globale = {
        "metadonnees": {
            "derniere_mise_a_jour": "2026-11-01",
            "statut": "Généré par le dépôt scrapeur"
        },
        "donnees_manuelles": donnees_manuelles
    }

    # Sauvegarde locale du fichier consolidé
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
