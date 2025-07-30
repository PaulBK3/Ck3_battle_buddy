import zipfile
import re
import csv
import os

SAVE_PATH = "test_save.ck3"
OUTPUT_CSV = "ck3_battles.csv"

def extract_gamestate(save_path):
    # Unzip the CK3 save to get the .gamestate file
    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith("gamestate"):
                zip_ref.extract(file)
                return os.path.join(file)
    return None

def parse_battles(gamestate_path):
    battles = []
    with open(gamestate_path, "r", encoding="utf-8") as f:
        data = f.read()

    # Regex to find battle blocks
    battle_blocks = re.findall(r"battle=\{(.*?)\n\}", data, re.DOTALL)

    for block in battle_blocks:
        name = re.search(r'name="(.*?)"', block)
        start_date = re.search(r'start_date="(.*?)"', block)
        end_date = re.search(r'end_date="(.*?)"', block)
        location = re.search(r'location=(\d+)', block)

        # Attacker and defender info
        attacker = re.search(r'attacker=\{(.*?)\}', block, re.DOTALL)
        defender = re.search(r'defender=\{(.*?)\}', block, re.DOTALL)

        def parse_side(side_block):
            if not side_block:
                return {"casualties": 0, "commander": None}
            casualties = re.search(r'casualties=(\d+)', side_block)
            commander = re.search(r'commander=(\d+)', side_block)
            return {
                "casualties": int(casualties.group(1)) if casualties else 0,
                "commander": commander.group(1) if commander else None
            }

        attacker_data = parse_side(attacker.group(1) if attacker else "")
        defender_data = parse_side(defender.group(1) if defender else "")

        battles.append({
            "name": name.group(1) if name else "Unknown",
            "start_date": start_date.group(1) if start_date else "",
            "end_date": end_date.group(1) if end_date else "",
            "location": location.group(1) if location else "",
            "attacker_commander": attacker_data["commander"],
            "attacker_casualties": attacker_data["casualties"],
            "defender_commander": defender_data["commander"],
            "defender_casualties": defender_data["casualties"]
        })

    return battles

def save_to_csv(battles, output_file):
    keys = battles[0].keys() if battles else []
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(battles)

def main():
    gamestate_path = extract_gamestate(SAVE_PATH)
    if gamestate_path:
        battles = parse_battles(gamestate_path)
        if battles:
            save_to_csv(battles, OUTPUT_CSV)
            print(f"Extracted {len(battles)} battles → {OUTPUT_CSV}")
        else:
            print("No battles found in save.")
    else:
        print("Failed to extract .gamestate file.")

if __name__ == "__main__":
    main()
