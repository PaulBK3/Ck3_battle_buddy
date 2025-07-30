import re
import csv

INPUT_FILE = "battleinfo"
OUTPUT_FILE = "battle_regiments.csv"

def parse_battles(text):
    rows = []

    # Each battle block like: 117440515={ ... }
    battle_blocks = re.findall(r'(\d+)=\{(.*?)\n\t\}', text, re.DOTALL)

    for battle_id, block in battle_blocks:
        # Get location
        location = re.search(r'location=(\d+)', block)
        location_id = location.group(1) if location else "unknown"

        # Parse each side
        for side_name in ["attacker", "defender"]:
            side_block_match = re.search(rf'{side_name}=\{{(.*?)\n\t\t\t\}}', block, re.DOTALL)
            if not side_block_match:
                continue
            side_block = side_block_match.group(1)

            commander = re.search(r'commander=(\d+)', side_block)
            commander_id = commander.group(1) if commander else "unknown"

            # Parse regiment_stats blocks inside side
            regiment_blocks = re.findall(r'\{\s*(.*?)\s*\}', side_block, re.DOTALL)
            for reg in regiment_blocks:
                regiment = {
                    "battle_id": battle_id,
                    "location": location_id,
                    "side": side_name,
                    "commander_id": commander_id,
                    "type": re.search(r'type=([^\s]+)', reg).group(1) if re.search(r'type=([^\s]+)', reg) else "unknown",
                    "knight": re.search(r'knight=(\d+)', reg).group(1) if re.search(r'knight=(\d+)', reg) else "none",
                    "initial_count": float(re.search(r'initial_count=(\d+)', reg).group(1)) if re.search(r'initial_count=(\d+)', reg) else 0,
                    "final_count": float(re.search(r'final_count=(\d+)', reg).group(1)) if re.search(r'final_count=(\d+)', reg) else 0,
                    "main_kills": float(re.search(r'main_kills=([\d\.]+)', reg).group(1)) if re.search(r'main_kills=([\d\.]+)', reg) else 0.0,
                    "pursuit_kills": float(re.search(r'pursuit_kills=([\d\.]+)', reg).group(1)) if re.search(r'pursuit_kills=([\d\.]+)', reg) else 0.0,
                    "main_losses": float(re.search(r'main_losses=([\d\.]+)', reg).group(1)) if re.search(r'main_losses=([\d\.]+)', reg) else 0.0,
                    "damage_last_tick": float(re.search(r'damage_last_tick=([\d\.]+)', reg).group(1)) if re.search(r'damage_last_tick=([\d\.]+)', reg) else 0.0
                }
                rows.append(regiment)
    return rows

# Read and parse file
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read()

rows = parse_battles(text)

# Save to CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

OUTPUT_FILE
