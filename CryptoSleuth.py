import requests
import datetime
from collections import defaultdict

BLOCKCHAIR_API = "https://api.blockchair.com/bitcoin/transactions"

def fetch_recent_transactions(limit=100):
    params = {
        "limit": limit
    }
    response = requests.get(BLOCKCHAIR_API, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("data", [])

def analyze_transaction_patterns(transactions):
    cluster_by_time = defaultdict(list)
    for tx in transactions:
        time_str = tx.get("time") or tx.get("block_time")
        amount = tx.get("fee_per_kb")
        if not time_str or not amount:
            continue
        dt = datetime.datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        hour = dt.replace(minute=0, second=0, microsecond=0)
        cluster_by_time[hour].append(amount)

    anomalies = []
    for hour, amounts in cluster_by_time.items():
        avg = sum(amounts) / len(amounts)
        if any(a > 5 * avg for a in amounts):
            anomalies.append((hour.isoformat(), max(amounts), avg))
    return anomalies

def run_sleuth():
    print("🔍 Получение последних транзакций Bitcoin...")
    txs = fetch_recent_transactions()
    print(f"Получено транзакций: {len(txs)}")
    anomalies = analyze_transaction_patterns(txs)
    if not anomalies:
        print("✅ Аномалий не обнаружено.")
    else:
        print("⚠ Обнаружены подозрительные аномалии:")
        for time, peak, avg in anomalies:
            print(f"  Время: {time} — Пик: {peak}, Среднее: {avg:.2f}")

if __name__ == "__main__":
    run_sleuth()
