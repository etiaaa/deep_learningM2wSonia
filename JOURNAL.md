# Journal methodologique

> Trace chronologique des decisions, travaux et corrections.
> A mettre a jour a chaque session de travail.

---

## 2026-04-30 &mdash; Cadrage initial

### Choix du sujet et du dataset

| | |
|---|---|
| **Dataset retenu** | HAM10000 (10 015 images dermatoscopiques, 7 classes) |
| **Domaine** | Dermatologie &mdash; classification mono-label de lesions cutanees |
| **Source** | Harvard Dataverse, DOI `10.7910/DVN/DBW86T` |
| **Reference** | Tschandl, Rosendahl & Kittler, *Scientific Data* (2018) |

**Justification :** desequilibre extreme (rapport ~60x entre classe majoritaire et minoritaire) qui repond directement a la question centrale du sujet sur l'apport reel d'un GAN ; enjeu clinique direct (faux negatif sur melanome = vie en jeu) ; biais d'acquisition documentes (regles graduees, encre, poils) exploitables en Grad-CAM.

**Datasets ecartes :**
- ChestX-ray14 &mdash; multi-label trop complexe, dilue l'effort sur le GAN
- APTOS 2019 &mdash; desequilibre moins marque (~10x au lieu de 60x)
- Camelyon16 &mdash; whole slide images trop lourdes pour Colab
- DIARETDB1 &mdash; volume trop faible (~89 images)
- Brain Tumor MRI / Malaria &mdash; trop equilibres, GAN moins justifie

### Setup technique

- **Stack :** Python 3.10, TensorFlow / Keras, scikit-learn, matplotlib / seaborn
- **Image size :** 224 x 224 (compatible VGG16 / ResNet50 ImageNet)
- **Batch size :** 32
- **Seeds :** fixees a 42 (`random`, `numpy`, `tensorflow`)
- **Notebook :** Jupyter

### Telechargement et indexation

- 3 fichiers recuperes depuis Harvard Dataverse (~2.7 Go total)
  - `HAM10000_metadata.csv` (converti depuis le `.tab`)
  - `HAM10000_images_part_1.zip` (5 000 images)
  - `HAM10000_images_part_2.zip` (5 015 images)
- Verification : **10 015 / 10 015 images resolues**, aucune manquante
- Distribution des classes confirmee :

```
nv     6 705  (66.9 %)
mel    1 113  (11.1 %)
bkl    1 099  (11.0 %)
bcc      514   (5.1 %)
akiec    327   (3.3 %)
vasc     142   (1.4 %)
df       115   (1.1 %)
```

### Audit qualite du dataset

| Aspect | Etat | Action |
|---|---|---|
| Labels | **Propres** &mdash; valides histopath / biopsie / suivi / expert | Aucune |
| Resolution | **Normalisee** &mdash; 600 x 450 RGB | Aucune |
| Doublons de lesions | **2 545 images** repliquees (7 470 lesions uniques) | **Split par `lesion_id`** |
| Ages manquants | 57 valeurs | Tagging `-1` |
| Artefacts (regles, encre, poils) | Presents | **Conserves** pour analyse Grad-CAM |

### Corrections appliquees

- [x] **Split stratifie par `lesion_id`** au lieu de `image_id` pour eviter le data leak (toutes les images d'une meme lesion vont dans le meme split)
- [x] Documentation explicite de la qualite du dataset dans une sous-section dediee
- [x] Tagging des 57 ages manquants (valeur `-1`)

### Nettoyage approfondi du dataset

Trois checks executes sur les 10 015 images via `clean_dataset.py` (~4 min CPU) :

| Check | Methode | Trouve | Action |
|---|---|---|---|
| **Doublons binaires** | hash MD5 | 4 images en 2 groupes (memes `lesion_id`) | Garder 1 par groupe, **exclure 2** |
| **Doublons visuels** | pHash 8x8 | 38 images en 19 groupes | 36 legitimes (memes lesion_id, gerees par split) ; **2 exclues** (lesion_id different = conflit d'annotation) |
| **Flou** | Variance Laplacien | 101 images dans le bottom 1% (blur < 15) | **Aucune exclusion** &mdash; mediane dataset (~50) coherente avec dermatoscopie ; exclure penaliserait disproportionnellement les classes rares (`vasc`, `df`) |

**Bilan** : 4 exclusions / 10 015 images (0,04 %).

### Architecture brut / clean

| | Chemin | Taille | Statut |
|---|---|---|---|
| **Brut** | `data/ham10000/` | 10 015 images | Intact, immuable |
| **Clean** | `data/ham10000_clean/HAM10000_metadata_clean.csv` | 10 011 lignes | Derive du brut |

### Livrables produits aujourd'hui

- `methodologie_HAM10000.ipynb` &mdash; notebook principal, sections 1 a 5 completes et executables
- `README.md` &mdash; pitch projet + arborescence + commande de lancement
- `requirements.txt` &mdash; dependances Python (+ `imagehash`, `opencv-python`)
- `JOURNAL.md` &mdash; ce fichier
- `clean_dataset.py` &mdash; script de nettoyage reproductible
- `data/ham10000/` &mdash; dataset brut extrait (10 015 jpg + metadata)
- `data/ham10000_clean/` &mdash; metadata clean + rapport + image_quality.csv

### Sections 6-15 construites

| # | Section | Contenu | Sauvegarde |
|---|---------|---------|------------|
| 6 | Baseline CNN | 3 blocs conv (16/32/64), helpers communs, class weights | `runs/01_baseline/` |
| 7 | CNN ameliore | 4 blocs conv (32/64/128/256), BN, dropout, data aug, GAP | `runs/02_improved/` |
| 8 | Transfer Learning | VGG16 + 2 phases (warmup tete &rarr; fine-tuning 4 dernieres couches) | `runs/03_transfer_learning/` |
| 9 | GAN | DCGAN 64x64 par classe rare (df, vasc), 100 epochs, sauvegarde generators | `runs/04_gan_*/` |
| 10 | Enrichissement | N=500 images synth par classe, sauvees dans `data/ham10000_synth/` | `data/ham10000_synth/` |
| 11 | Reentrainement | VGG16 reentraine sur train enrichi, meme protocole | `runs/05_vgg_enriched/` |
| 12 | Evaluation | Tableau synthese, barplots F1 par classe, courbes overlay, 4 matrices confusion | inline |
| 13 | Grad-CAM | Implementation, 3 categories (reussis / errones / biais detectes via Hough) | inline |
| 14 | Discussion critique | 3 scenarios GAN, 5 limites, faisabilite clinique, ameliorations possibles | inline |
| 15 | Conclusion | Synthese, 5 enseignements cles, perspectives | inline |

### Notebook final

- **50 cellules** au total : 23 markdown + 27 code
- Toutes les sorties (modeles `.keras`, historiques JSON, metriques JSON, images PNG) sauvees dans `runs/`
- Reproductible : seeds fixees, helpers reutilises, splits stratifies par lesion_id avec assertions

### Runtime attendu (a titre indicatif)

| Bloc | GPU | CPU |
|------|-----|-----|
| Baseline (20 epochs) | ~10 min | ~1-2 h |
| CNN ameliore (25 epochs) | ~15 min | ~2-3 h |
| Transfer Learning (10+15 epochs) | ~20 min | ~3-4 h |
| GAN (2 classes x 100 epochs) | ~15 min | ~1.5 h |
| Reentrainement (10+15 epochs) | ~25 min | ~4 h |
| **Total** | **~1.5 h** | **~10-15 h** |

&rarr; Recommandation : Colab GPU ou Kaggle Notebooks (T4 gratuit).

---

## 2026-05-18 — Run reel + finalisation

### Auteurs identifies

- **SAI Sonia** + **SAKOA Etia-Anaelle** (M2 YNOV Data Scientist)

### Run d'entrainement reel execute

Run complet sur CPU (Python 3.13, TF 2.21, Windows), IMG_SIZE = 160 (reduit de 224 pour tenir sur CPU sans GPU). Total : **~80 min** (47 min run principal + 37 min finition GAN vasc + retrain).

### Resultats observes

| Modele | Accuracy | Balanced acc. | F1 macro |
|--------|----------|---------------|----------|
| Baseline CNN          | **0.584** | 0.242 | 0.148 |
| CNN ameliore          | 0.477 | 0.280 | 0.183 |
| **VGG16 Transfer Learning** | 0.364 | **0.316** | **0.206** |
| VGG16 + GAN enrichi   | 0.548 | 0.286 | 0.196 |

**Verdict GAN** : SCENARIO C (degradation sur les classes ciblees)

- F1 sur `df`   : 0.067 -> 0.000 (-100 %)
- F1 sur `vasc` : 0.440 -> 0.083 (-81 %)

Mais effet secondaire positif : amelioration sur `akiec` (+51 %), `bcc` (+57 %), `bkl` (+83 %), `nv` (+32 %). Le GAN a agi comme regulariseur indirect plutot que comme specialiste des classes rares.

Cause probable : DCGAN sur 80-100 images = mode collapse partiel, gap de resolution 64 -> 160 introduisant un biais texture, ratio synth/reel 6:1 desequilibre.

### Mises a jour notebook

- [x] Page de garde : auteurs reels + promo 2025-2026
- [x] Cellule config : IMG_SIZE 224 -> 160 documente
- [x] Tableau pretraitement : 160x160 explique
- [x] Section 12 : tableau de synthese statique avec vrais chiffres + F1 par classe
- [x] Section 14 : scenario C tranche, causes detaillees, effets secondaires positifs documentes

### Livrables finaux pousses sur GitHub (etiaaa/deep_learningM2wSonia)

- README.md, JOURNAL.md
- methodologie_HAM10000.ipynb (50 cellules)
- clean_dataset.py, requirements.txt
- data/ham10000/HAM10000_metadata.csv + data/ham10000_clean/*

Modeles entraines (`runs/`) et images brutes (`data/ham10000/HAM10000_images_part_*/`) exclus via .gitignore pour des raisons de taille (regenerables).
