# Rapport de nettoyage HAM10000

> Genere automatiquement le 2026-04-30.
> Source brute : `data/ham10000/` (10 015 images, intacte)
> Resultat clean : `data/ham10000_clean/HAM10000_metadata_clean.csv` (10011 images)

## Methodologie

Trois checks executes sur les 10 015 images :

1. **Hash MD5** &mdash; detection des doublons binaires exacts.
2. **Perceptual hash (pHash 8x8)** &mdash; detection des doublons visuels.
3. **Variance Laplacien** &mdash; detection du flou.

## Resultats des checks

### Doublons MD5

- **4 images** dans **2 groupes** de doublons binaires exacts.
- Tous partagent le meme `lesion_id` &mdash; il s'agit du meme cliche uploade en double.
- **Action :** on garde 1 image par groupe, on exclut les autres.

### Doublons perceptuels (pHash)

- **38 images** dans **19 groupes**.
- Decomposition :
  - **Legitimes** (meme `lesion_id`) : 36 images. Ce sont des photos differentes de la meme lesion (angles, zoom). On les garde &mdash; le split par `lesion_id` evite tout leak.
  - **Suspects** (lesion_ids differents mais image visuellement identique) : 2 images. Possible erreur d'annotation. On les exclut par precaution.

### Flou (variance Laplacien)

- Mediane globale : **49.2** &mdash; cohérent avec la dermatoscopie (eclairage doux, peu de transitions nettes).
- Bottom 1 % (blur < 15) : **101 images**, reparties sur toutes les classes y compris les rares (`vasc`: 4, `df`: 2).
- **Decision :** on n'exclut pas ces images. Justification :
  - La distribution de flou n'est pas anormale pour ce type d'imagerie.
  - Exclure 4 images de `vasc` (3 % de la classe) ou 2 de `df` (2 %) sacrifierait des donnees rares.
  - Le flou sera traite implicitement par les augmentations et le modele.

## Bilan

| | Brut | Exclu | Clean |
|---|---|---|---|
| **Images** | 10 015 | 4 | 10011 |
| **Lesions uniques** | 7 470 | 4 | 7469 |

Distribution par classe (clean) :

```
dx
nv       6701
mel      1113
bkl      1099
bcc       514
akiec     327
vasc      142
df        115
```

## Fichiers produits

- `HAM10000_metadata_clean.csv` &mdash; metadonnees filtrees (10011 lignes)
- `excluded_images.csv` &mdash; images exclues avec raison
- `image_quality.csv` &mdash; quality scores complets pour les 10 015 images
- `analysis_summary.json` &mdash; statistiques agregees
- `cleaning_report.md` &mdash; ce fichier

## Pour utiliser le clean

```python
metadata = pd.read_csv('data/ham10000_clean/HAM10000_metadata_clean.csv')
# les chemins d'images pointent toujours vers data/ham10000/HAM10000_images_part_*/
```
