import os
import json
import subprocess
import sys
import requests
import base64
from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def install_playwright_browsers():
    """Télécharge tous les navigateurs Playwright nécessaires s'ils manquent."""
    print("Vérification/Installation des navigateurs Playwright...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
    except Exception as e:
        print(f"Note sur l'installation : {e}")

def run_scraper():
    # 1. S'assure que les navigateurs sont installés
    install_playwright_browsers()
    
    print("Démarrage du scraper sur Render...")
    
    # 2. Scraping avec Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Exemple de navigation (à adapter avec tes sites cibles)
        # page.goto("https://www.fournisseur-exemple.fr", wait_until="networkidle")
        
        browser.close()

    # 3. Données de test / récupérées
    nouveaux_tarifs = {
        "derniere_mise_a_jour": "2026-11-01",
        "statut": "Données récupérées avec succès via le scraper"
    }
    
    json_str = json.dumps(nouveaux_tarifs, indent=2, ensure_ascii=False)
    
    # 4. Envoi automatique vers ton dépôt principal (GitHub Pages)
    push_to_main_repo(json_str)

def push_to_main_repo(content_json_str):
    token = os.environ.get("GH_TOKEN")
    repo = "absinthe1975/comparateur-energie"
    path = "data.json"
    
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    message = "Mise à jour automatique des tarifs via le Scraper Render"
    content_b64 = base64.b64encode(content_json_str.encode()).decode()
    
    data = {
        "message": message,
        "content": content_b64
    }
    if sha:
        data["sha"] = sha
        
    put_res = requests.put(url, json=data, headers=headers)
    if put_res.status_code in [200, 201]:
        print("Succès : Le fichier data.json a été mis à jour sur le site principal !")
    else:
        print(f"Erreur lors du push GitHub : {put_res.text}")

@app.route("/")
def home():
    # Permet de lancer le scraper manuellement en visitant l'URL de ton service Render
    run_scraper()
    return "Scraper exécuté avec succès et fichier mis à jour !"

if __name__ == "__main__":
    # Exécute le scraper une première fois au démarrage du service
    try:
        run_scraper()
    except Exception as e:
        print(f"Erreur lors du premier lancement : {e}")
        
    # Garde le serveur web éveillé pour satisfaire Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
