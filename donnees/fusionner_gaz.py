import json
import os

# Chemins des fichiers (tous situés dans le dossier "donnees/")
dossier = "donnees"
chemin_gaz = os.path.join(dossier, "tarifs_manuels_gaz.json")
chemin_consolide = os.path.join(dossier, "grille_consolidee.json")

def fusionner_gaz():
    # 1. Charger le fichier de gaz manuel
    if not os.path.exists(chemin_gaz):
        print(f"Erreur : Le fichier {chemin_gaz} est introuvable.")
        return
    
    with open(chemin_gaz, "r", encoding="utf-8") as f:
        data_gaz = json.load(f)

    # 2. Charger la grille consolidée existante
    if not os.path.exists(chemin_consolide):
        print(f"Erreur : Le fichier {chemin_consolide} est introuvable.")
        return
        
    with open(chemin_consolide, "r", encoding="utf-8") as f:
        grille_actuelle = json.load(f)

    # 3. Injecter les données de gaz au bon endroit
    # D'après ta structure, les données manuelles sont souvent imbriquées 
    # dans "donnees_manuelles_et_confirmees" ou à la racine de la grille.
    if "donnees_manuelles_et_confirmees" in grille_actuelle:
        cible = grille_actuelle["donnees_manuelles_et_confirmees"]
    else:
        cible = grille_actuelle

    # Mise à jour de la liste des offres de gaz et des abonnements
    cible["gas"] = data_gaz.get("gas", [])
    if "abo_g" in data_gaz:
        cible.setdefault("abo_g", {}).update(data_gaz["abo_g"])

    # 4. Sauvegarder la grille consolidée mise à jour
    with open(chemin_consolide, "w", encoding="utf-8") as f:
        json.dump(grille_actuelle, f, ensure_ascii=False, indent=2)

    print("Succès : Les grilles de gaz ont été fusionnées dans grille_consolidee.json !")

if __name__ == "__main__":
    fusionner_gaz()
