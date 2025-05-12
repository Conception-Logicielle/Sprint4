#!/bin/bash

if ! command -v zenity &> /dev/null; then
    echo "Zenity n'est pas installé. Installe-le avec : sudo apt install zenity"
    exit 1
fi

FICHIER_PDF=$(zenity --file-selection --title="Choisis un ou plusieurs fichiers PDF" --file-filter="*.pdf" --multiple --separator="|")
if [ -z "$FICHIER_PDF" ]; then
    zenity --error --text="Abandon. Aucun fichier n'a été sélectionné..."
    exit 1
fi

DOSSIER_TEXTE="./corpus_txt"
DOSSIER_RESUMES="./resumes"

mkdir -p "$DOSSIER_TEXTE"
mkdir -p "$DOSSIER_RESUMES"

(
echo "Conversion des fichiers PDF en texte avec pdftotext.sh..."

if [ ! -x ./pdftotext.sh ]; then
    echo "Le script pdftotext.sh est introuvable ou non exécutable."
    exit 1
fi

IFS="|" read -ra fichiers_array <<< "$FICHIER_PDF"
for fichier_pdf in "${fichiers_array[@]}"; do
    nom_fichier=$(basename "$fichier_pdf" .pdf)
    fichier_txt="$DOSSIER_TEXTE/$nom_fichier.txt"

    if [ -f "$fichier_txt" ]; then
        echo "Le fichier $fichier_txt existe déjà, conversion ignorée."
        continue
    fi

    echo "Conversion de $fichier_pdf"
    ./pdftotext.sh "$fichier_pdf" "$DOSSIER_TEXTE"

    if [ $? -ne 0 ]; then
        echo "Erreur lors de la conversion de $fichier_pdf"
        continue
    fi

    echo "Fichier $fichier_pdf converti avec succès."
done

echo "Conversion et mise en page terminées pour tous les fichiers."

echo "Génération des fichiers de résumés..."

cd extractInfo/main || exit 1

if [ "$1" == "-x" ]; then
  cargo run --release ../../corpus_txt ../../resumes xml
else
  cargo run --release ../../corpus_txt ../../resumes txt
fi

) | zenity --progress --title="Traitement des fichiers" --text="Traitement en cours..." --pulsate --auto-close --width=500 --height=100

if [ $? -eq 0 ]; then
    zenity --info --text="Traitement terminé avec succès."
else
    zenity --error --text="Une erreur est survenue pendant le traitement."
fi
