import zipfile
import regex
import csv
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import dashboard

#INPUT_FILE = "battleinfo"
SAVE_PATH = "test_save2.ck3"

def extract_gamestate(save_path):
    # Unzip the CK3 save to get the .gamestate file
    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith("gamestate"):
                zip_ref.extract(file)
                return os.path.join(file)
    return None

def parse_battles(text):
    battles = {
        "battles": []
    }
    combats = regex.findall(r'(combat_results)=(\{(?:[^(){}]+|(?2))*+\})', text, regex.DOTALL)
    # Each battle block like: 117440515={ ... }

    battle_blocks = regex.findall(r'(\d+)=(\{(?:[^(){}]+|(?2))*+\})', combats[0][1], regex.DOTALL)

    for battle_id, block in battle_blocks:
        # Get location
        location = regex.search(r'location=(\d+)', block)
        location_id = location.group(1) if location else "unknown"
        battle = {
            "battle_id": battle_id,
            "location": location_id,
            "sides": []
        }
        # Parse each side
        for side_name in ["attacker", "defender"]:
            side_block_match = regex.search(rf'{side_name}=\{{(.*?)\n\t\t\t\}}', block, regex.DOTALL)
            if not side_block_match:
                continue
            side_block = side_block_match.group(1)

            commander = regex.search(r'commander=(\d+)', side_block)
            commander_id = commander.group(1) if commander else "unknown"
            battle_side = {
                    "side": side_name,
                    "commander_id": commander_id,
                    "regiments" : []
            }
            # Parse regiment_stats blocks inside side
            regiment_blocks = regex.findall(r'\{\s*(.*?)\s*\}', side_block, regex.DOTALL)
            for reg in regiment_blocks:
                regiment = {
                    "type": regex.search(r'type=([^\s]+)', reg).group(1) if regex.search(r'type=([^\s]+)', reg) else "unknown",
                    "knight": regex.search(r'knight=(\d+)', reg).group(1) if regex.search(r'knight=(\d+)', reg) else "none",
                    "initial_count": float(regex.search(r'initial_count=(\d+)', reg).group(1)) if regex.search(r'initial_count=(\d+)', reg) else 0,
                    "final_count": float(regex.search(r'final_count=(\d+)', reg).group(1)) if regex.search(r'final_count=(\d+)', reg) else 0,
                    "main_kills": float(regex.search(r'main_kills=([\d\.]+)', reg).group(1)) if regex.search(r'main_kills=([\d\.]+)', reg) else 0.0,
                    "pursuit_kills": float(regex.search(r'pursuit_kills=([\d\.]+)', reg).group(1)) if regex.search(r'pursuit_kills=([\d\.]+)', reg) else 0.0,
                    "main_losses": float(regex.search(r'main_losses=([\d\.]+)', reg).group(1)) if regex.search(r'main_losses=([\d\.]+)', reg) else 0.0,
                    "pursuit_losses_self": float(regex.search(r'pursuit_losses_self=([\d\.]+)', reg).group(1)) if regex.search(r'pursuit_losses_self=([\d\.]+)', reg) else 0.0,
                    "pursuit_losses_maa": float(regex.search(r'pursuit_losses_maa=([\d\.]+)', reg).group(1)) if regex.search(r'pursuit_losses_maa=([\d\.]+)', reg) else 0.0,
                    "damage_last_tick": float(regex.search(r'damage_last_tick=([\d\.]+)', reg).group(1)) if regex.search(r'damage_last_tick=([\d\.]+)', reg) else 0.0
                }
                battle_side["regiments"].append(regiment)
            battle["sides"].append(battle_side)
        battles["battles"].append(battle)
    return battles



def main():
    gamestate_path = extract_gamestate(SAVE_PATH)
    if gamestate_path:
         # Read and parse file
        with open(gamestate_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        print("Failed to extract .gamestate file.")
   

    battles = parse_battles(text)
    # Flatten JSON into a DataFrame
    rows = []
    for battle in battles["battles"]:
        for side in battle["sides"]:
            for reg in side["regiments"]:
                rows.append({
                    "battle_id": battle["battle_id"],
                    "location": battle["location"],
                    "side": side["side"],
                    "commander": side["commander_id"],
                    **reg
                })

    df = pd.DataFrame(rows)

    df["total_kills"] = df["main_kills"] + df["pursuit_kills"]
    top_commanders = df.groupby("commander")["total_kills"].sum().sort_values(ascending=False).head(10)
    top_commanders.plot(kind="bar", title="Top 10 Commanders by Kills")
    plt.show()

    print(json.dumps(battles, indent=4))

    dashboard.dashboard(battles)
    # Save to CSV
    #with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        #writer = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter=';')
        #writer.writeheader()
        #writer.writerows(rows)

if __name__ == "__main__":
    main()
