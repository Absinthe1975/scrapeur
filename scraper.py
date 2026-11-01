import os
import json
import base64
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration GitHub (récupérée de manière sécurisée depuis les variables d'environnement Render)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "Absinthe1975/scrapeur")  # Ex: "TonPseudo/ton-repo"
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

    # 1. Vérifier si le fichier existe déjà pour récupérer son SHA (obligatoire pour l'API GitHub)
    r = requests.get(url, headers=headers)
    sha = None
    if r.status_code == 200:
        sha = r.json().get("sha")

    # 2. Préparer la requête de mise à jour / création
    data = {
        "message": "Mise à jour automatique de la grille consolidée via Render",
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
    print("=== Démarrage de la consolidation globale ===")

    # Chemin exact vers ton fichier manuel dans le dossier donnees
    chemin_manuel = os.path.join("donnees", "tarifs_manuels.json")
    donnees_manuelles = {}
    
    if os.path.exists(chemin_manuel):
        try:
            with open(chemin_manuel, "r", encoding="utf-8") as f:
                donnees_manuelles = json.load(f)
            print("Succès : Fichier 'tarifs_manuels.json' chargé depuis le dossier donnees.")
        except json.JSONDecodeError:
            print("Attention : Le fichier 'tarifs_manuels.json' est vide ou mal formaté. Utilisation d'une structure vide.")
            donnees_manuelles = {}
    else:
        print(f"Attention : Fichier introuvable à l'emplacement {chemin_manuel}")

    # Structure de la grille globale unifiée
    grille_globale = {
        "metadonnees": {
            "derniere_mise_a_jour": "2026-11-01",
            "statut": "Consolidation hybride (Données manuelles et officielles)"
        },
        "donnees_manuelles_et_confirmees": donnees_manuelles
    }

    # Sauvegarde locale du fichier consolidé dans le dossier donnees
    os.makedirs("donnees", exist_ok=True)
    fichier_sortie = os.path.join("donnees", "grille_consolidee.json")
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(grille_globale, f, indent=2, ensure_ascii=False)
        
    print(f"Fichier global '{fichier_sortie}' mis à jour localement avec succès !")

    # Synchronisation automatique sur GitHub
    push_to_github(fichier_sortie, "donnees/grille_consolidee.json")

@app.route("/")
def home():
    """Déclenche la consolidation lorsque tu visites l'URL de ton service Render"""
    try:
        run_consolidation()
        return """
        <h2>Consolidation exécutée avec succès !</h2>
        <p>Le fichier <b>grille_consolidee.json</b> a été mis à jour et synchronisé.</p>
        <p><a href='/telecharger' target='_blank' style='font-size: 18px; color: blue;'>👉 Cliquer ici pour voir / télécharger le fichier JSON unifié</a></p>
        """
    except Exception as e:
        return f"Erreur durant l'exécution : {e}", 500

@app.route("/telecharger")
def telecharger():
    """Permet de voir ou télécharger directement le fichier JSON unifié depuis le navigateur"""
    fichier_sortie = os.path.join("donnees", "grille_consolidee.json")
    if os.path.exists(fichier_sortie):
        with open(fichier_sortie, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return "Le fichier consolidé n'a pas encore été généré. Visitez la page d'accueil d'abord.", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
