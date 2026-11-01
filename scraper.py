import os
import json
from flask import Flask

app = Flask(__name__)

def run_consolidation():
    print("=== Démarrage de la consolidation globale ===")

    # Chemin exact vers ton fichier manuel dans le dossier donnees
    chemin_manuel = os.path.join("donnees", "tarifs_manuels.json")
    donnees_manuelles = {}
    
    if os.path.exists(chemin_manuel):
        with open(chemin_manuel, "r", encoding="utf-8") as f:
            donnees_manuelles = json.load(f)
        print("Succès : Fichier 'tarifs_manuels.json' chargé depuis le dossier donnees.")
    else:
        print(f"Attention : Fichier introuvable à l'emplacement {chemin_manuel}")

    # Structure de la grille globale unifiée
    grille_globale = {
        "metadonnees": {
            "derniere_mise_a_jour": "2026-11-01",
            "statut": "Consolidation hybride (Données sécurisées)"
        },
        "donnees_manuelles_et_confirmees": donnees_manuelles
    }

    # Sauvegarde du fichier consolidé dans le dossier donnees
    fichier_sortie = os.path.join("donnees", "grille_consolidee.json")
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(grille_globale, f, indent=2, ensure_ascii=False)
        
    print(f"Fichier global '{fichier_sortie}' mis à jour avec succès !")

@app.route("/")
def home():
    """Déclenche la consolidation lorsque tu visites l'URL de ton service Render"""
    try:
        run_consolidation()
        return "Consolidation des tarifs exécutée avec succès ! Le fichier grille_consolidee.json est à jour."
    except Exception as e:
        return f"Erreur durant l'exécution : {e}", 500

if __name__ == "__main__":
    # Flask démarre instantanément, évitant le timeout et l'erreur de port fermé sur Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
