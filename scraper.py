import os
import json
import base64
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration GitHub (récupérée de manière sécurisée depuis les variables d'environnement Render)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "Absinthe1975/scrapeur")
GITHUB_BRANCH = "main"

def push_to_github(file_path, repo_path):
    """Pousse automatiquement un fichier sur le dépôt GitHub"""
    if not GITHUB_TOKEN:
        print("Note : GITHUB_TOKEN non configuré, la synchronisation GitHub est ignorée.")
        return False

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{repo_path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    with open(file_path, "rb") as f:
        content_bytes = f.read()
    content_encoded = base64.b64encode(content_bytes).decode("utf-8")

    # 1. Vérifier si le fichier existe déjà pour récupérer son SHA
    r = requests.get(url, headers=headers)
    sha = None
    if r.status_code == 200:
        sha = r.json().get("sha")

    # 2. Préparer la requête de mise à jour / création
    data = {
        "message": "Mise à jour automatique de la grille consolidée et des sources via Render",
        "content": content_encoded,
        "branch": GITHUB_BRANCH
    }
    if sha:
        data["sha"] = sha

    # 3. Envoyer à l'API GitHub
    put_response = requests.put(url, headers=headers, json=data)
    if put_response.status_code in [200, 201]:
        print(f"Succès : Fichier '{repo_path}' poussé sur GitHub !")
        return True
    else:
        print(f"Erreur lors du push GitHub : {put_response.status_code} - {put_response.text}")
        return False

def run_consolidation():
    print("=== Démarrage de la consolidation globale avec sources == data ===")

    # 1. Chargement des tarifs manuels
    chemin_manuel = os.path.join("donnees", "tarifs_manuels.json")
    donnees_manuelles = {}
    if os.path.exists(chemin_manuel):
        try:
            with open(chemin_manuel, "r", encoding="utf-8") as f:
                donnees_manuelles = json.load(f)
            print("Succès : Fichier 'tarifs_manuels.json' chargé.")
        except json.JSONDecodeError:
            print("Attention : 'tarifs_manuels.json' mal formaté.")

    # 2. Chargement ou intégration des sources et liens (sources.json)
    sources_data = {
        "provider": "gemini",
        "model": "gemini-3.1-flash-lite",
        "tarifs_pages": {
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
            "octo": "https://prix-elec.com/fournisseurs/octopus-energy/offres",
            "alpiq": "https://prix-elec.com/fournisseurs/alpiq/offres",
            "ohm": "https://prix-elec.com/fournisseurs/ohm-energie/offres",
            "happe": "https://prix-elec.com/fournisseurs/happ-e/offres",
            "engie": "https://prix-elec.com/fournisseurs/engie/offres",
            "ilek": "https://prix-elec.com/fournisseurs/ilek/offres",
            "enercoop": "https://prix-elec.com/fournisseurs/enercoop/offres"
        }
    }

    # Structure globale unifiée intégrant les tarifs et le référentiel des sources
    grille_globale = {
        "metadonnees": {
            "derniere_mise_a_jour": "2026-11-01",
            "statut": "Consolidation hybride (Tarifs et Sources intégrés)"
        },
        "referentiel_sources": sources_data,
        "donnees_manuelles_et_confirmees": donnees_manuelles
    }

    # Sauvegarde locale
    os.makedirs("donnees", exist_ok=True)
    fichier_sortie = os.path.join("donnees", "grille_consolidee.json")
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(grille_globale, f, indent=2, ensure_ascii=False)
        
    print(f"Fichier global '{fichier_sortie}' mis à jour localement avec succès !")

    # Synchronisation automatique sur GitHub
    push_to_github(fichier_sortie, "donnees/grille_consolidee.json")

@app.route("/")
def home():
    try:
        run_consolidation()
        return """
        <h2>Consolidation globale et des sources exécutée avec succès !</h2>
        <p>Le fichier <b>grille_consolidee.json</b> intègre désormais toutes les données et les liens de référence.</p>
        <p><a href='/telecharger' target='_blank' style='font-size: 18px; color: blue;'>👉 Voir / Télécharger le JSON unifié complet</a></p>
        """
    except Exception as e:
        return f"Erreur durant l'exécution : {e}", 500

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
