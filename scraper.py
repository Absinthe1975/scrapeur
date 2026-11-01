import os
import json
import base64
import time
import random
import requests
from flask import Flask, jsonify
from playwright.sync_api import sync_playwright

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
        "message": "Mise à jour automatique sécurisée",
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
    <h2>🚀 Mon Comparateur - Mode Sécurisé</h2>
    <p>Le serveur fonctionne correctement.</p>
    <p><a href='/telecharger' target='_blank' style='font-size: 18px; color: blue;'>👉 Voir / Télécharger le JSON consolidé</a></p>
    <p><a href='/actualiser' style='font-size: 16px; color: green;'>🔄 Lancer l'actualisation</a></p>
    """

@app.route("/actualiser")
def actualiser():
    try:
        chemin_manuel = os.path.join("donnees", "tarifs_manuels.json")
        donnees_manuelles = {}
        if os.path.exists(chemin_manuel):
            try:
                with open(chemin_manuel, "r", encoding="utf-8") as f:
                    donnees_manuelles = json.load(f)
            except:
                pass

        # Restreignons temporairement aux sites clés pour éviter le timeout sur Render
        tarifs_pages = {
            "ekw": "https://prix-elec.com/fournisseurs/ekwateur/offres",
            "total": "https://prix-elec.com/fournisseurs/totalenergies/offres",
            "edf": "https://prix-elec.com/fournisseurs/edf/offres",
            "engie": "https://particuliers.engie.fr/",
            "ilek": "https://www.ilek.fr/grilles-tarifaires"
        }

        resultats = {}
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=random.choice(user_agents))
            page = context.new_page()

            for fournisseur, url in tarifs_pages.items():
                statut_final = "erreur"
                code_final = 0
                try:
                    res = requests.get(url, headers={"User-Agent": random.choice(user_agents)}, timeout=4)
                    code_final = res.status_code
                    if res.status_code == 200:
                        statut_final = "code_200_requests"
                    else:
                        response_pw = page.goto(url, timeout=8000, wait_until="domcontentloaded")
                        code_val = response_pw.status if response_pw else code_final
                        statut_final = f"code_{code_val}_playwright"
                        code_final = code_val
                except Exception as ex:
                    statut_final = f"erreur: {str(ex)}"

                resultats[fournisseur] = {"statut": statut_final, "code": code_final}

            browser.close()

        grille_globale = {
            "metadonnees": {
                "derniere_mise_a_jour": "2026-11-01",
                "statut": "Consolidation optimisée sans timeout"
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
        <h3>Mise à jour effectuée avec succès sans dépassement de délai !</h3>
        <p><a href='/'>Retour à l'accueil</a> | <a href='/telecharger' target='_blank'>Voir le JSON</a></p>
        """
    except Exception as e:
        return f"<h3>⚠️ Erreur interne attrapée :</h3><pre>{str(e)}</pre><p><a href='/'>Retour</a></p>", 500

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
