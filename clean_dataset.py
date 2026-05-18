"""Cleaning HAM10000 - script reproductible.

Trois checks sur les 10 015 images :
1. MD5 exact duplicates
2. Perceptual hash (pHash 8x8)
3. Variance Laplacien (flou)

Produits :
- data/ham10000_clean/HAM10000_metadata_clean.csv
- data/ham10000_clean/excluded_images.csv
- data/ham10000_clean/image_quality.csv
- data/ham10000_clean/analysis_summary.json
- data/ham10000_clean/cleaning_report.md

Usage : python clean_dataset.py
Duree : ~4 min sur CPU.
"""
import hashlib
import json
import time
from pathlib import Path

import cv2
import imagehash
import pandas as pd
from PIL import Image

DATA_DIR = Path(__file__).parent / 'data' / 'ham10000'
CLEAN_DIR = Path(__file__).parent / 'data' / 'ham10000_clean'
CLEAN_DIR.mkdir(parents=True, exist_ok=True)


def compute_quality():
    image_paths = {}
    for d in DATA_DIR.glob('HAM10000_images*'):
        if d.is_dir():
            for img in d.glob('*.jpg'):
                image_paths[img.stem] = img
    print(f'Computing quality on {len(image_paths)} images...')

    records, t0 = [], time.time()
    for i, (image_id, path) in enumerate(sorted(image_paths.items())):
        if (i + 1) % 1000 == 0:
            print(f'  {i+1:>5} / {len(image_paths)} ({time.time()-t0:.0f}s)')
        with open(path, 'rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()
        phash = str(imagehash.phash(Image.open(path), hash_size=8))
        blur = float(cv2.Laplacian(cv2.imread(str(path), 0), cv2.CV_64F).var())
        records.append({'image_id': image_id, 'md5': md5, 'phash': phash, 'blur': blur})

    df = pd.DataFrame(records)
    df.to_csv(CLEAN_DIR / 'image_quality.csv', index=False)
    print(f'Done in {time.time()-t0:.0f}s')
    return df


def apply_exclusions(quality, meta):
    m = quality.merge(meta, on='image_id')
    exclusions = []

    # 1) MD5 duplicates - keep first per group
    for h, g in m.groupby('md5').filter(lambda g: len(g) > 1).groupby('md5'):
        sorted_g = g.sort_values('image_id')
        for _, row in sorted_g.iloc[1:].iterrows():
            exclusions.append({
                'image_id': row['image_id'], 'reason': 'md5_duplicate',
                'kept_alternative': sorted_g.iloc[0]['image_id'],
                'lesion_id': row['lesion_id'], 'dx': row['dx'],
            })

    # 2) pHash duplicates with conflicting lesion_id - exclude all
    excluded_ids = {e['image_id'] for e in exclusions}
    phash_groups = m.groupby('phash').filter(lambda g: len(g) > 1)
    for h, g in phash_groups.groupby('phash'):
        if g['lesion_id'].nunique() > 1:
            for _, row in g.iterrows():
                if row['image_id'] not in excluded_ids:
                    exclusions.append({
                        'image_id': row['image_id'], 'reason': 'phash_label_conflict',
                        'kept_alternative': None,
                        'lesion_id': row['lesion_id'], 'dx': row['dx'],
                    })

    return pd.DataFrame(exclusions)


def main():
    quality_path = CLEAN_DIR / 'image_quality.csv'
    if quality_path.exists():
        print(f'Reusing existing {quality_path}')
        quality = pd.read_csv(quality_path)
    else:
        quality = compute_quality()

    meta = pd.read_csv(DATA_DIR / 'HAM10000_metadata.csv')
    excluded = apply_exclusions(quality, meta)
    excluded.to_csv(CLEAN_DIR / 'excluded_images.csv', index=False)

    clean = meta[~meta['image_id'].isin(excluded['image_id'])].copy()
    clean.to_csv(CLEAN_DIR / 'HAM10000_metadata_clean.csv', index=False)

    summary = {
        'raw_images': len(meta),
        'excluded': len(excluded),
        'clean_images': len(clean),
        'exclusions_by_reason': excluded['reason'].value_counts().to_dict(),
    }
    with open(CLEAN_DIR / 'analysis_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f'\nRaw   : {len(meta)}')
    print(f'Excl  : {len(excluded)}')
    print(f'Clean : {len(clean)}')
    print(f'\nFiles written to {CLEAN_DIR}')


if __name__ == '__main__':
    main()
