# Documents/OCR framework

La milestone 6 fournit un pipeline local et déterministe pour construire des
fixtures de documents sans service externe.

## Source et vérité terrain

Chaque source JSON contient un identifiant, le rendu texte canonique et un objet
`ground_truth`. Le schéma est [`schemas/document-source.schema.json`](../schemas/document-source.schema.json).
Le générateur conserve ces deux éléments dans `source.txt` et
`ground-truth.json`, puis écrit un `manifest.json` avec seed, dimensions, DPI et
empreinte SHA-256 de chaque variante.

## Variantes raster

`runner.document_dataset` rend un bitmap grayscale PGM avec une police 5×7
déterministe. Chaque dataset contient les variantes `digital-300dpi`,
`digital-150dpi`, `rotated-300dpi`, `noisy-150dpi` et `compressed-150dpi`.
La compression est une quantification grayscale reproductible et indépendante
d'un codec. Les mêmes pixels peuvent être convertis plus tard en PNG/JPEG/PDF
pour une campagne OCR équipée.

```powershell
python scripts/generate_document_dataset.py datasets/documents/invoice-001.json .tmp/invoice-001
```

Le générateur refuse un dossier de sortie non vide afin de ne jamais écraser un
jeu de données existant.

## Tâches de la milestone 9

La catégorie Documents est complète avec dix tâches. DOC-01 à DOC-05 évaluent le
post-traitement de rendus numériques et de transcriptions OCR déterministes :
300/150 DPI, rotation, bruit et formats numériques locaux. DOC-06 et DOC-07
couvrent respectivement les tableaux et formulaires, DOC-08 les documents
multi-pages, DOC-09 les types mélangés et DOC-10 l'extraction JSON complexe.

Les tâches DOC-01 à DOC-05, DOC-08 et DOC-09 utilisent des transcriptions texte
portables dans leur workspace. Elles ne prétendent pas remplacer une campagne
OCR native : les invariants mesurés sont les champs, dates, identifiants,
montants, cellules et erreurs de parsing. Les variantes PGM produites par le
générateur restent disponibles pour les campagnes équipées d'un OCR.

## Scoring

`runner.document_metrics` calcule CER/WER par distance de Levenshtein sans
normalisation silencieuse. `score_fields` conserve les champs manquants et
hallucinés et sépare les précisions exactes, numériques, dates, identifiants et
cellules de tableaux. La validité JSON et la validité par schéma sont des
métriques séparées.

```powershell
python scripts/score_document.py --expected .tmp/invoice-001/ground-truth.json --actual candidate.json --reference-text .tmp/invoice-001/source.txt --hypothesis-text candidate.txt
```

Les sorties sont des métriques brutes JSON et ne sont pas agrégées en score
unique. L'exécution OCR native (Tesseract ou moteur hébergé) reste un adaptateur
de campagne : l'absence de Tesseract sur la machine de développement ne bloque
ni la génération ni le scoring.

DOC-10 exécute aussi le scoring des champs après la fin du feedback modèle et
des validations. La vérité terrain reste sous `private-tests/`, et les métriques
structurées sont inscrites au résultat brut du run. Cela mesure l'extraction
texte-vers-structure, pas la reconnaissance visuelle de PDF ou d'images.
