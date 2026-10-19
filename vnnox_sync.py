import requests
import os

# ÚDAJE ZO SUPABASE A VNNOX
SUPABASE_URL = "https://rxxmcwrznuliziukvehr.supabase.co"
SUPABASE_KEY = "sb_publishable_wXSVVmEexpgcm-aBZB5u1g_Ya5hWz9F"

VNNOX_API_URL = "https://api-eu.vnnox.com"
VNNOX_USER = "stregl"
VNNOX_PASS = "z318rk"

supabase_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def get_vnnox_token():
    url = f"{VNNOX_API_URL}/v2/login"
    payload = {"username": VNNOX_USER, "password": VNNOX_PASS}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("token") or data.get("token")
    except Exception as e:
        print(f"Chyba pri prihlasovaní do VNNOX: {e}")
    return None

def sync_screens():
    token = get_vnnox_token()
    if not token:
        print("Nepodarilo sa získať VNNOX token.")
        return

    vnnox_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    screens_url = f"{VNNOX_API_URL}/v2/player/list"
    try:
        res = requests.get(screens_url, headers=vnnox_headers, timeout=10)
        if res.status_code == 200:
            players = res.json().get("data", [])
            print(f"Nájdených prehrávačov z VNNOX: {len(players)}")
            
            for player in players:
                player_id = player.get("id") or player.get("playerId")
                player_name = player.get("name", f"Obrazovka {player_id}")
                is_online = player.get("status") in [1, True, "ONLINE", "online"]

                device_data = {
                    "id": player_id,
                    "name": player_name,
                    "status": "online" if is_online else "offline",
                    "last_ping": "now()"
                }

                r = requests.post(
                    f"{SUPABASE_URL}/rest/v1/devices",
                    json=device_data,
                    headers=supabase_headers
                )
                print(f"Aktualizované: {player_name} -> {'ONLINE' if is_online else 'OFFLINE'} (Status code: {r.status_code})")
        else:
            print(f"Chyba VNNOX API: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Chyba pri komunikácii s VNNOX: {e}")

if __name__ == "__main__":
    sync_screens()
