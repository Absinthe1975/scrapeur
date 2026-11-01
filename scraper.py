import os
import json
import base64
import time
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration GitHub
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

    r = requests.get(url, headers=headers)
    sha = None
    if r.status_code == 200:
        sha = r.json().get("sha")

    data = {
        "message": "Mise à jour automatique de la grille consolidée (mode ralenti anti-surcharge)",
        "content": content_encoded,
        "branch": GITHUB_BRANCH
    }
    if sha:
        data["sha"] = sha

    put_response = requests.put(url, headers=headers, json=data)
    if put_response.status_code in [200, 201]:
        print(f"Succès : Fichier '{repo_path}' poussé sur GitHub !")
        return True
    else:
        print(f"Erreur lors du push GitHub : {put_response.status_code} - {put_response.text}")
        return False

def run_consolidation_avec_ralenti():
    print("=== Démarrage de la consolidation avec limitation de vitesse (Anti-Rate Limit) ===")

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

    # 2. Référentiel des pages à aller chercher (basé sur tes sources)
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

    resultats_scraping_ralenti = {}
    headers_requete = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("--- Début de la lecture des sources avec pause de courtoisie entre chaque site ---")
    for fournisseur, url in tarifs_pages.items():
        try:
            print(f"Interrogation de {fournisseur} ({url})...")
            # Envoi de la requête avec un User-Agent pour passer certains filtres basiques
            reponse = requests.get(url, headers=headers_requete, timeout=10)
            
            if reponse.status_code == 200:
                resultats_scraping_ralenti[fournisseur] = {"statut": "accessible", "code": 200}
            else:
                resultats_scraping_ralenti[fournisseur] = {"statut": f"code_erreur_{reponse.status_code}", "code": reponse.status_code}
        except requests.exceptions.Timeout:
            print(f"⚠️ Timeout pour {fournisseur} (site trop lent).")
            resultats_scraping_ralenti[fournisseur] = {"statut": "timeout"}
        except Exception as e:
            print(f"⚠️ Erreur pour {fournisseur} : {e}")
            resultats_scraping_ralenti[fournisseur] = {"statut": "erreur_technique"}

        # 🐢 RALENTISSEMENT : On fait une pause de 3 secondes pour ne pas surcharger les serveurs (évite les erreurs 429)
        time.sleep(3)

    # Structure globale unifiée
    grille_globale = {
        "metadonnees": {
            "derniere_mise_a_jour": "2026-11-01",
            "statut": "Consolidation hybride avec mode ralenti (anti-surcharge)"
        },
        "tests_accessibilite_sources": resultats_scraping_ralenti,
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
        run_consolidation_avec_ralenti()
        return """
        <h2>Consolidation avec ralenti exécutée avec succès !</h2>
        <p>Le script a interrogé les sources en prenant son temps pour éviter les blocages (erreurs 429) et mis à jour GitHub.</p>
        <p><a href='/telecharger' target='_blank' style='font-size: 18px; color: blue;'>👉 Voir / Télécharger le JSON consolidé</a></p>
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
