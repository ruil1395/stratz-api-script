import requests
import json
import sys

# --- 1. ВАШИ НАСТРОЙКИ ---
API_KEY = "СЮДА_ВСТАВЬТЕ_ВАШ_API_КЛЮЧ"

# --- 2. КОНФИГУРАЦИЯ API ---
API_URL = "https://api.stratz.com/graphql"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def fetch_match_data(match_id: int):
    """
    Отправляет запрос к API Stratz и выводит информацию о матче.
    """
    print(f"🔎 Отправка запроса для матча с ID: {match_id}...")

    if "СЮДА_ВСТАВЬТЕ" in API_KEY or not API_KEY:
        print("\n❌ ОШИБКА: Пожалуйста, отредактируйте файл stratz_script.py и вставьте ваш API-ключ в переменную API_KEY.")
        return

    graphql_query = {
        "query": """
        query GetMatchDetails($matchId: Long!) {
          match(id: $matchId) {
            id didRadiantWin durationSeconds radiantKills direKills
            players {
              steamAccount { name proSteamAccount { name } }
              hero { displayName }
              isRadiant kills deaths assists goldPerMinute
            }
          }
        }
        """,
        "variables": {"matchId": match_id}
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(graphql_query))
        response.raise_for_status()
        data = response.json()

        if 'errors' in data:
            print(f"\n❌ ОШИБКА ОТ API STRATZ: {data['errors'][0]['message']}")
            return

        match_data = data.get('data', {}).get('match')
        if not match_data:
            print("\n❌ Не удалось найти данные по указанному матчу. Проверьте ID.")
            return

        print("\n" + "="*50 + "\n✅ ИНФОРМАЦИЯ О МАТЧЕ\n" + "="*50)
        
        winner = "Radiant" if match_data['didRadiantWin'] else "Dire"
        print(f"\n🔹 Победитель: {winner}")
        print(f"🔹 Длительность: {match_data['durationSeconds'] // 60} мин {match_data['durationSeconds'] % 60} сек")
        print(f"🔹 Счет: Radiant {sum(match_data['radiantKills'])} - {sum(match_data['direKills'])} Dire")

        for is_radiant_team in [True, False]:
            team_name = "Radiant" if is_radiant_team else "Dire"
            print("\n" + "-"*30 + f"\nКоманда {team_name}\n" + "-"*30)
            for player in match_data['players']:
                if player['isRadiant'] == is_radiant_team:
                    player_name = (player['steamAccount'].get('proSteamAccount') or {}).get('name') or player['steamAccount'].get('name') or "Аноним"
                    print(f"  - {player_name:<20} | {player['hero']['displayName']:<15} | KDA: {player['kills']}/{player['deaths']}/{player['assists']:<7} | GPM: {player['goldPerMinute']}")
        print("\n" + "="*50)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ОШИБКА СЕТИ: {e}")
    except Exception as e:
        print(f"\n❌ НЕПРЕДВИДЕННАЯ ОШИБКА: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ ОШИБКА: Пожалуйста, укажите ID матча при запуске скрипта.")
        print("Пример: python stratz_script.py 8679779216")
    else:
        try:
            match_id_from_command = int(sys.argv[1])
            fetch_match_data(match_id_from_command)
        except ValueError:
            print("❌ ОШИБКА: ID матча должен быть числом.")

