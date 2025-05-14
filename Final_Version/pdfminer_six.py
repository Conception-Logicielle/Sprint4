import os
from pathlib import Path
from pdfminer.high_level import extract_text
import re

# Nettoie le texte brut : enlève les doublons de lignes vides et d'espaces
def nettoyer_texte(texte):
    texte = re.sub(r'\n{2,}', '\n\n', texte)  # garde max 1 ligne vide entre paragraphes
    texte = re.sub(r' {2,}', ' ', texte)      # réduit les espaces multiples
    return texte.strip()

# Détecte les sections importantes dans le texte (titre, résumé, etc.)
# et les met en majuscules pour les repérer facilement
def detecter_sections(texte):
    sections = [
        "abstract", "résumé", "introduction", "state of the art", "méthode", "method",
        "experiments", "results", "discussion", "conclusion", "references", "bibliography"
    ]
    lignes = texte.splitlines()
    lignes_nettoyées = []
    for ligne in lignes:
        l = ligne.strip()
        # Si une ligne correspond à un titre de section, on la passe en majuscules
        if any(re.match(rf'^\s*{s}[ .:–-]*$', l.lower()) for s in sections):
            lignes_nettoyées.append(l.upper())
        else:
            lignes_nettoyées.append(l)
    return "\n".join(lignes_nettoyées)

# Fonction principale : convertit un PDF en fichier texte propre
def convertir_pdf_en_txt(pdf_path, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = Path(pdf_path)

    try:
        texte = extract_text(pdf_path, laparams=None)  # extraction du texte brut
        texte = nettoyer_texte(texte)                  # nettoyage
        texte = detecter_sections(texte)               # repérage des sections

        txt_path = output_dir / (pdf_path.stem + ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(texte)
        print(f"[OK] Converti : {pdf_path.name} --> {txt_path.name}")
    except Exception as e:
        print(f"[ERR] Erreur avec {pdf_path.name} : {e}")

# Lancement du script
if __name__ == "__main__":
    # Dossier des PDF à traiter
    dossier_pdfs = Path(__file__).resolve().parent.parent / "CORPUS_TRAIN"
    # Dossier de sortie pour les fichiers texte
    dossier_txts = "corpus_txt_nettoye"
    os.makedirs(dossier_txts, exist_ok=True)

    # Boucle sur tous les PDF du dossier
    for fichier in os.listdir(dossier_pdfs):
        if fichier.endswith(".pdf"):
            convertir_pdf_en_txt(os.path.join(dossier_pdfs, fichier), dossier_txts)
