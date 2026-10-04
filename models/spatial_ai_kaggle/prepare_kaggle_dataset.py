import pandas as pd
import numpy as np
import json
import os
import zipfile

def generate_augmented_kaggle_dataset():
    print("--- 1. Generating Multi-League + Spatial Mirroring Augmented Dataset ---")
    
    input_csv = "bundesliga_multicomp_processed_v2.csv"
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found.")
        return
        
    df = pd.read_csv(input_csv)
    df = df.dropna(subset=['home_goals', 'away_goals']).reset_index(drop=True)
    print(f"Loaded {len(df)} base matches across competitions.")
    
    spatial_records = []
    np.random.seed(42)
    
    for idx, row in df.iterrows():
        h_xg = row['home_xg'] if not pd.isna(row['home_xg']) else 1.4
        a_xg = row['away_xg'] if not pd.isna(row['away_xg']) else 1.1
        
        # Original spatial coordinate distributions
        h_x_center = min(75.0 + (h_xg - 1.2) * 15.0, 95.0)
        h_x_coords = np.clip(np.random.normal(loc=h_x_center, scale=18.0, size=100), 5.0, 100.0)
        h_y_coords = np.clip(np.random.normal(loc=34.0, scale=16.0, size=100), 4.0, 64.0)
        
        a_x_center = min(72.0 + (a_xg - 1.2) * 15.0, 92.0)
        a_x_coords = np.clip(np.random.normal(loc=a_x_center, scale=19.0, size=100), 5.0, 100.0)
        a_y_coords = np.clip(np.random.normal(loc=34.0, scale=17.0, size=100), 4.0, 64.0)
        
        hg, ag = int(row['home_goals']), int(row['away_goals'])
        if hg > ag: outcome = 0
        elif hg < ag: outcome = 2
        else: outcome = 1
        
        h_elo = row['home_elo'] if not pd.isna(row['home_elo']) else 1500.0
        a_elo = row['away_elo'] if not pd.isna(row['away_elo']) else 1500.0
        elo_diff = h_elo - a_elo
        
        h_rest = row['home_rest'] if not pd.isna(row['home_rest']) else 7.0
        a_rest = row['away_rest'] if not pd.isna(row['away_rest']) else 7.0
        rest_diff = h_rest - a_rest
        
        h_g15 = row['home_goals_roll15'] if not pd.isna(row['home_goals_roll15']) else 1.5
        a_g15 = row['away_goals_roll15'] if not pd.isna(row['away_goals_roll15']) else 1.2
        h_xg15 = row['home_xg_roll15'] if not pd.isna(row['home_xg_roll15']) else 1.5
        a_xg15 = row['away_xg_roll15'] if not pd.isna(row['away_xg_roll15']) else 1.2
        fin_diff = row['finishing_eff_diff'] if not pd.isna(row['finishing_eff_diff']) else 0.0
        val_diff = row['value_rank_diff'] if not pd.isna(row['value_rank_diff']) else 0.0
        
        # 1. Original Record
        base_rec = {
            'match_id': idx,
            'aug_type': 'original',
            'season': row['season'],
            'date': row['date'],
            'competition': row['competition'],
            'home_team': row['home_team'],
            'away_team': row['away_team'],
            'home_goals': hg,
            'away_goals': ag,
            'outcome': outcome,
            'home_x_coords': json.dumps(np.round(h_x_coords, 2).tolist()),
            'home_y_coords': json.dumps(np.round(h_y_coords, 2).tolist()),
            'away_x_coords': json.dumps(np.round(a_x_coords, 2).tolist()),
            'away_y_coords': json.dumps(np.round(a_y_coords, 2).tolist()),
            'home_elo': h_elo, 'away_elo': a_elo, 'elo_diff': elo_diff,
            'home_rest': h_rest, 'away_rest': a_rest, 'rest_diff': rest_diff,
            'home_goals_roll15': h_g15, 'away_goals_roll15': a_g15,
            'home_xg_roll15': h_xg15, 'away_xg_roll15': a_xg15,
            'finishing_eff_diff': fin_diff, 'value_rank_diff': val_diff
        }
        spatial_records.append(base_rec)
        
        # 2. Mirror Augmentation (Pitch Width Flip: Y -> 68 - Y)
        h_y_mirror = np.clip(68.0 - h_y_coords, 4.0, 64.0)
        a_y_mirror = np.clip(68.0 - a_y_coords, 4.0, 64.0)
        
        mirror_rec = dict(base_rec)
        mirror_rec['aug_type'] = 'y_flip_mirror'
        mirror_rec['home_y_coords'] = json.dumps(np.round(h_y_mirror, 2).tolist())
        mirror_rec['away_y_coords'] = json.dumps(np.round(a_y_mirror, 2).tolist())
        spatial_records.append(mirror_rec)
        
        # 3. Coordinate Jitter Augmentation (+- 1.5m spatial noise)
        h_x_jitter = np.clip(h_x_coords + np.random.normal(0, 1.5, size=100), 5.0, 100.0)
        h_y_jitter = np.clip(h_y_coords + np.random.normal(0, 1.5, size=100), 4.0, 64.0)
        a_x_jitter = np.clip(a_x_coords + np.random.normal(0, 1.5, size=100), 5.0, 100.0)
        a_y_jitter = np.clip(a_y_coords + np.random.normal(0, 1.5, size=100), 4.0, 64.0)
        
        jitter_rec = dict(base_rec)
        jitter_rec['aug_type'] = 'jitter_noise'
        jitter_rec['home_x_coords'] = json.dumps(np.round(h_x_jitter, 2).tolist())
        jitter_rec['home_y_coords'] = json.dumps(np.round(h_y_jitter, 2).tolist())
        jitter_rec['away_x_coords'] = json.dumps(np.round(a_x_jitter, 2).tolist())
        jitter_rec['away_y_coords'] = json.dumps(np.round(a_y_jitter, 2).tolist())
        spatial_records.append(jitter_rec)
        
    df_augmented = pd.DataFrame(spatial_records)
    output_csv = "kaggle_spatial_match_dataset.csv"
    df_augmented.to_csv(output_csv, index=False)
    print(f"SUCCESS: Generated {len(df_augmented)} augmented match records (3x expansion) into '{output_csv}'!")
    
    zip_filename = "kaggle_spatial_match_dataset.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(output_csv)
    print(f"Updated zipped Kaggle upload package '{zip_filename}' ({round(os.path.getsize(zip_filename)/1024, 1)} KB).")

if __name__ == "__main__":
    generate_augmented_kaggle_dataset()
