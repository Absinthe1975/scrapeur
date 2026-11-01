import os
import json
import base64
import time
import random
import requests
from flask import Flask, jsonify

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "Absinthe1975/scrapeur")
GITHUB_BRANCH = "main"

def push_to_github(file_path, repo_path):
    if not GITHUB_TOKEN:
        return False
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{repo_path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    with open(file_path, "rb") as f:
        content_bytes = f.read()
    content_encoded = base64.b64encode(content_bytes).decode("utf-8")

    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None

    data = {
        "message": "Mise à jour automatique de la grille consolidée (anti-blocage)",
        "content": content_encoded,
        "branch": GITHUB_BRANCH
    }
    if sha:
        data["sha"] = sha

    put_response = requests.put(url, headers=headers, json=data)
    return put_response.status_code in [200, 201]

@app.route("/")
def home():
    return """
    <h2>🚀 Mon Comparateur - Service Actif</h2>
    <p>Le serveur fonctionne correctement.</p>
    <p><a href='/telecharger' target='_blank' style='font-size: 18px; color: blue;'>👉 Voir / Télécharger le JSON consolidé</a></p>
    <p><a href='/actualiser' style='font-size: 16px; color: green;'>🔄 Lancer une mise à jour optimisée (contournement)</a></p>
    """

@app.route("/actualiser")
def actualiser():
    chemin_manuel = os.path.join("donnees", "tarifs_manuels.json")
    donnees_manuelles = {}
    if os.path.exists(chemin_manuel):
        try:
            with open(chemin_manuel, "r", encoding="utf-8") as f:
                donnees_manuelles = json.load(f)
        except:
            pass

    tarifs_pages = {
        "ekw": "https://prix-elec.com/fournisseurs/ekwateur/offres",
        "total": "https://prix-elec.com/fournisseurs/totalenergies/offres",
        "geg": "https://prix-elec.com/fournisseurs/geg/offres",
        "gdb": "https://prix-elec.com/fournisseurs/gaz-de-bordeaux/offres",
        "plen": "https://prix-elec.com/fournisseurs/plenitude/offres",
        "llum": "https://prix-elec.com/fournisseurs/llum/offres",
        "dyneff": "https://prix-elec.com/fournisseurs/dyneff/offres",
        "mint": "https://prix-elec.com/fournisseurs/mint-energie/offres",
        "primeo": "https://prix-elec.com/fournisseurs/primeo/offres",
        "alterna": "https://prix-elec.com/fournisseurs/alterna/offres",
        "edf": "https://prix-elec.com/fournisseurs/edf/offres",
        "octo": "https://octopusenergy.fr/offre-electricite-tarifs",
        "alpiq": "https://prix-elec.com/fournisseurs/alpiq/offres",
        "ohm": "https://prix-elec.com/fournisseurs/ohm-energie/offres",
        "happe": "https://prix-elec.com/fournisseurs/happ-e/offres",
        "engie": "https://particuliers.engie.fr/",
        "ilek": "https://www.ilek.fr/grilles-tarifaires",
        "enercoop": "https://www.faq.enercoop.fr/hc/fr/articles/360024967152-Annexes-tarifaires"
    }

    resultats = {}
    
    # Liste de User-Agents réalistes pour simuler différents navigateurs et éviter le blocage net
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]

    for fournisseur, url in tarifs_pages.items():
        try:
            # En-têtes complets imitant un navigateur moderne
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.google.com/",
                "Connection": "keep-alive"
            }
            reponse = requests.get(url, headers=headers, timeout=8)
            resultats[fournisseur] = {"statut": f"code_{reponse.status_code}", "code": reponse.status_code}
        except:
            resultats[fournisseur] = {"statut": "erreur_ou_timeout"}
        
        # Pause aléatoire entre 2 et 4 secondes pour paraître plus naturel
        time.sleep(random.uniform(2.0, 4.0))

    grille_globale = {
        "metadonnees": {
            "derniere_mise_a_jour": "2026-11-01",
            "statut": "Consolidation hybride avec en-têtes furtifs"
        },
        "tests_accessibilite_sources": resultats,
        "donnees_manuelles_et_confirmees": donnees_manuelles
    }

    os.makedirs("donnees", exist_ok=True)
    fichier_sortie = os.path.join("donnees", "grille_consolidee.json")
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(grille_globale, f, indent=2, ensure_ascii=False)

    push_to_github(fichier_sortie, "donnees/grille_consolidee.json")

    return """
    <h3>Mise à jour furtive effectuée avec succès !</h3>
    <p><a href='/'>Retour à l'accueil</a> | <a href='/telecharger' target='_blank'>Voir le JSON</a></p>
    """

@app.route("/telecharger")
def telecharger():
    fichier_sortie = os.path.join("donnees", "grille_consolidee.json")
    if os.path.exists(fichier_sortie):
        with open(fichier_sortie, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return "Le fichier consolidé n'a pas encore été généré.", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
