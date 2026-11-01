import os
import json
import subprocess
import sys
import requests
import base64
from playwright.sync_api import sync_playwright

def install_playwright_browsers():
    """Télécharge Chromium s'il n'est pas présent sur l'instance."""
    print("Vérification/Installation des navigateurs Playwright...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

def run_scraper():
    # 1. S'assure que Chromium est installé avant de le lancer
    install_playwright_browsers()
    
    print("Démarrage du scraper sur Render...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

def run_scraper():
    print("Démarrage du scraper sur Render...")
    
    # Exemple de récupération de données via Playwright (contourne les robots.txt)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Exemple fictif d'une page que tu veux visiter :
        # page.goto("https://www.fournisseur-exemple.fr", wait_until="networkidle")
        # html = page.content()
        
        browser.close()

    # Dictionnaire de données simulé/récupéré pour l'exemple
    nouveaux_tarifs = {
        "derniere_mise_a_jour": "2026-11-01",
        "statut": "Données récupérées avec succès via le scraper"
    }
    
    # Conversion en texte JSON
    json_str = json.dumps(nouveaux_tarifs, indent=2, ensure_ascii=False)
    
    # Envoi automatique vers ton dépôt principal (Ton site GitHub Pages)
    push_to_main_repo(json_str)

def push_to_main_repo(content_json_str):
    token = os.environ.get("GH_TOKEN")
    repo = "absinthe1975/comparateur-energie" # Ton dépôt principal (change si le nom exact diffère)
    path = "data.json" # Le fichier de données de ton site
    
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    
    # Récupération du SHA actuel du fichier pour autoriser la modification
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    # Préparation de l'envoi
    message = "Mise à jour automatique des tarifs via le Scraper Render"
    content_b64 = base64.b64encode(content_json_str.encode()).decode()
    
    data = {
        "message": message,
        "content": content_b64
    }
    if sha:
        data["sha"] = sha
        
    # Publication de la mise à jour sur ton site principal
    put_res = requests.put(url, json=data, headers=headers)
    if put_res.status_code in [200, 201]:
        print("Succès : Le fichier data.json a été mis à jour sur le site principal !")
    else:
        print(f"Erreur lors du push GitHub : {put_res.text}")

if __name__ == "__main__":
    run_scraper()
