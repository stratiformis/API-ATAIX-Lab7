import json
import requests
import time

# === Константы ===
API_KEY = ""
API_BASE_URL = "https://api.ataix.kz/api/orders"
ORDERS_FILE = "orders_data.json"


# === Работа с JSON-файлом ===
def load_orders():
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)


def save_orders(order_list):
    with open(ORDERS_FILE, "w") as f:
        json.dump(order_list, f, indent=4)


# === Работа с API ===
def get_order_status(order_id):
    url = f"{API_BASE_URL}/{order_id}"
    headers = {
        "accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code == 200:
        return response.json().get("result", {}).get("status")

    print(f"❌ Ошибка получения статуса ордера {order_id}: {response.status_code}")
    return None


def create_new_order(symbol, price):
    new_price = round(float(price) * 1.02, 4)  # 2% дороже от купленной цены

    data = {
        "symbol": symbol,
        "side": "sell",
        "type": "limit",
        "quantity": 1,
        "price": str(new_price)
    }
    headers = {
        "accept": "application/json",
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(API_BASE_URL, headers=headers, json=data, timeout=20)

    # Логируем полный ответ для отладки
    print(f"Ответ от API при создании ордера на продажу: {response.status_code} {response.text}")

    if response.status_code == 200:
        return response.json().get("result")

    print(f"❌ Ошибка при создании нового ордера: {response.status_code}")
    return None


# === Основной процесс ===
def process_orders():
    orders = load_orders()
    new_orders = []

    for order in orders:
        order_id = order.get("orderID")
        print(f"\n🔍 Проверка ордера {order_id}...")

        # Получаем статус ордера
        status = get_order_status(order_id)

        # Если ордер уже выполнен, создаем ордер на продажу
        if status == "filled":
            print(f"✅ Ордер {order_id} выполнен. Создаём ордер на продажу.")
            new_order = create_new_order(order["symbol"], order["price"])

            if new_order:
                print(f"➕ Новый ордер на продажу создан: {new_order['orderID']} по цене {new_order['price']}")
                new_orders.append({
                    "orderID": new_order["orderID"],
                    "price": new_order["price"],
                    "quantity": new_order["quantity"],
                    "symbol": new_order["symbol"],
                    "created": new_order["created"],
                    "status": new_order["status"]
                })
        else:
            print(f"⚠️ Ордер {order_id} не выполнен или не найден. Статус: {status}")

        time.sleep(1)

    # Добавляем новые ордера в основной список и сохраняем
    orders.extend(new_orders)
    save_orders(orders)
    print("\n📁 Обработка завершена. Файл orders_data.json обновлён.")


# === Запуск ===
if __name__ == "__main__":
    process_orders()
