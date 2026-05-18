# Projet final Deep Learning

**Classification d'images dermatoscopiques** &mdash; CNN, Transfer Learning, Grad-CAM, GAN.
Master 2 YNOV &mdash; Data Science / Intelligence Artificielle.

---

## Le projet en une phrase

Construire et comparer trois niveaux de classifieurs sur le dataset **HAM10000** (10 015 images, 7 classes), expliquer leurs decisions via **Grad-CAM**, puis evaluer si un **GAN** entraine sur les classes rares ameliore reellement les performances sans introduire de biais.

## Structure

```
delivrables/
├── README.md                          <- ce fichier
├── JOURNAL.md                         <- journal methodologique
├── methodologie_HAM10000.ipynb        <- livrable principal (15 sections, 50 cellules)
├── clean_dataset.py                   <- script de nettoyage (reproductible)
├── requirements.txt                   <- dependances
├── data/
│   ├── ham10000/                      <- BRUT (intact, 10 015 images)
│   │   ├── HAM10000_metadata.csv
│   │   ├── HAM10000_images_part_1/    (5 000 images)
│   │   └── HAM10000_images_part_2/    (5 015 images)
│   ├── ham10000_clean/                <- CLEAN (derive du brut)
│   │   ├── HAM10000_metadata_clean.csv  (10 011 lignes apres exclusions)
│   │   ├── excluded_images.csv
│   │   ├── image_quality.csv
│   │   ├── analysis_summary.json
│   │   └── cleaning_report.md
│   └── ham10000_synth/                <- SYNTHETIQUE (produit par le notebook section 10)
│       ├── df/                          (500 images generees par DCGAN)
│       └── vasc/                        (500 images generees par DCGAN)
└── runs/                              <- Sorties d'entrainement (produit par le notebook)
    ├── 01_baseline/                     (model.keras, history.json, metrics.json)
    ├── 02_improved/
    ├── 03_transfer_learning/
    ├── 04_gan_df/                       (generator.keras, samples.png, losses.json)
    ├── 04_gan_vasc/
    └── 05_vgg_enriched/
```

> **Brut vs clean** : le brut est immuable (source de verite). Le clean est *derive* automatiquement par `clean_dataset.py` et utilise par le notebook.

## Comment lancer

```bash
pip install -r requirements.txt
python clean_dataset.py              # ~4 min : produit data/ham10000_clean/
jupyter notebook methodologie_HAM10000.ipynb
```

Le dataset est deja telecharge dans `data/ham10000/`. Si tu repars de zero, la cellule de telechargement utilise `kagglehub` ; sinon recupere les fichiers depuis Harvard Dataverse (DOI `10.7910/DVN/DBW86T`).

### Runtime attendu

| Bloc | GPU (T4) | CPU |
|------|----------|-----|
| Sections 1-5 (data + EDA) | < 1 min | < 1 min |
| Section 6 baseline (20 epochs) | ~10 min | ~1-2 h |
| Section 7 CNN ameliore (25 epochs) | ~15 min | ~2-3 h |
| Section 8 Transfer Learning (10+15 epochs) | ~20 min | ~3-4 h |
| Section 9 GAN (2 classes x 100 epochs) | ~15 min | ~1.5 h |
| Section 11 reentrainement (10+15 epochs) | ~25 min | ~4 h |
| Sections 12-15 (analyse) | < 5 min | < 5 min |
| **Total** | **~1h30** | **~10-15 h** |

> **Recommandation** : ouvrir le notebook dans **Google Colab** (GPU T4 gratuit) ou **Kaggle Notebooks**.

## Architecture pedagogique

| Bloc | Sections | Objectif |
|------|----------|----------|
| **Cadrage**       | 01-05 | Probleme, dataset, pretraitement, EDA |
| **Modeles**       | 06-08 | Baseline -> CNN ameliore -> Transfer Learning |
| **GAN**           | 09-11 | Generation synthetique, enrichissement, reentrainement |
| **Analyse**       | 12-15 | Comparaison, Grad-CAM, discussion critique, conclusion |

## Reproductibilite

- Toutes les graines aleatoires sont fixees a **42**.
- Split stratifie **70 / 15 / 15** (train / val / test).
- Les images synthetiques generees par GAN n'enrichissent **que** le set d'entrainement.
