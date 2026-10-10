"""
Harvest and cache all Understat matches for Bundesliga seasons 2021-2022 through 2025-2026.
Uses soccerdata's TLS session with ThreadPoolExecutor for fast caching.
"""

import os
import time
import concurrent.futures
import soccerdata as sd

def cache_all_seasons():
    print("=== Downloading and caching all Bundesliga Understat matches ===")
    seasons = ['2021-2022', '2022-2023', '2023-2024', '2024-2025', '2025-2026']
    
    us = sd.Understat(leagues='GER-Bundesliga', seasons=seasons)
    sched = us.read_schedule().reset_index()
    print(f"Total schedule entries across {len(seasons)} seasons: {len(sched)}")
    
    uncached = []
    for idx, row in sched.iterrows():
        filepath = us.data_dir / f"match_{row['game_id']}.json"
        if not filepath.exists():
            uncached.append((row['url'], row['game_id']))
            
    print(f"Matches already cached: {len(sched) - len(uncached)}")
    print(f"Matches to download: {len(uncached)}")
    
    if not uncached:
        print("All matches are already cached!")
        return
        
    start_time = time.time()
    success = 0
    errors = 0
    
    def fetch_match(item):
        url, match_id = item
        try:
            res = us._read_match(url, match_id)
            return True if res is not None else False
        except Exception as e:
            return False
            
    # Use 8 worker threads for fast TLS requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_match, item) for item in uncached]
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            if future.result():
                success += 1
            else:
                errors += 1
            if (i + 1) % 100 == 0 or (i + 1) == len(uncached):
                elapsed = time.time() - start_time
                print(f"Progress: {i+1}/{len(uncached)} matches ({success} success, {errors} errors) in {elapsed:.1f}s")
                
    total_time = time.time() - start_time
    print(f"=== Complete: {success} downloaded, {errors} errors in {total_time:.1f}s ===")

if __name__ == "__main__":
    cache_all_seasons()
