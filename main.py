import requests
import time
import json

# Cargar configuración
with open("config.json") as f:
    config = json.load(f)

TELEGRAM_TOKEN = config["telegram_token"]
CHAT_ID = config["telegram_user_id"]
MONEDAS = config["monedas"]
INTERVALO = config["intervalo_segundos"]
LIMITES = config["limites"]

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)

def obtener_ofertas(moneda, tipo):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "asset": moneda,
        "fiat": "BOB",
        "merchantCheck": False,
        "page": 1,
        "rows": 5,
        "payTypes": [],
        "publisherType": None,
        "tradeType": tipo
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        return []

def verificar_ofertas():
    for moneda in MONEDAS:
        for tipo in ["BUY", "SELL"]:
            ofertas = obtener_ofertas(moneda, tipo)
            for oferta in ofertas:
                precio = float(oferta["adv"]["price"])
                nombre = oferta["advertiser"]["nickName"]
                link = f"https://p2p.binance.com/es/advertiserDetail?advertiserNo={oferta['advertiser']['userNo']}"

                if tipo == "BUY" and precio <= LIMITES[moneda]["buy_max"]:
                    msg = f"💱 *{tipo}* oferta de *{moneda}*\n👤 Vendedor: `{nombre}`\n💵 Precio: *{precio}*\n🔗 [Ver oferta]({link})"
                    enviar_telegram(msg)

                if tipo == "SELL" and precio >= LIMITES[moneda]["sell_min"]:
                    msg = f"💱 *{tipo}* oferta de *{moneda}*\n👤 Comprador: `{nombre}`\n💵 Precio: *{precio}*\n🔗 [Ver oferta]({link})"
                    enviar_telegram(msg)

while True:
    try:
        verificar_ofertas()
    except Exception as e:
        enviar_telegram(f"❌ Error en bot: {e}")
    time.sleep(INTERVALO)
