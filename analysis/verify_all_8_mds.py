import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

with open('data/all_matchdays_11_der_woche.json', 'r', encoding='utf-8') as f:
    totw_dataset = json.load(f)

with open('data/bundesliga_lineups_md1_8.json', 'r', encoding='utf-8') as f:
    lineups_db = json.load(f)

print("=== VERIFYING ALL 8 MATCHDAYS ===")
print(f"Total matchdays: {len(totw_dataset)}")

for md_num in range(1, 9):
    md_str = str(md_num)
    assert md_str in totw_dataset, f"Missing MD {md_str}"
    data = totw_dataset[md_str]
    lineup = data["lineup"]
    jokers = data["jokers"]
    
    assert len(lineup) == 11, f"MD {md_str} must have 11 players in lineup (got {len(lineup)})"
    assert len(jokers) == 3, f"MD {md_str} must have 3 jokers (got {len(jokers)})"
    
    # Check starters
    subs_list = [s["name"] for s in lineups_db.get(md_str, {}).get("substitutes", [])]
    for p in lineup:
        assert p["name"] not in subs_list, f"FATAL: Substitute {p['name']} found in Starting 11 for MD {md_str}!"
        assert "Starter" in p["highlight"], f"Player {p['name']} must denote Starter status"
        assert 0 <= p["x"] <= 100 and 0 <= p["y"] <= 100, f"Coords out of bounds for {p['name']}"
        
    for j in jokers:
        assert 1 <= j["rank"] <= 3
        assert "Eingewechselt" in j["min_in"]
        
    print(f"  [OK] MD {md_str} ({data['formation']}): 11 Starters verified, 3 Jokers verified. MVP: {data['mvp']}")

print("\n[ALL 8 MATCHDAYS 100% VERIFIED AND COMPLIANT!]")
