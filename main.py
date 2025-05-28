import json
import requests
import time

with open("config.json") as f:
    config = json.load(f)

def buscar_ofertas(moneda, tipo, max_precio):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    data = {
        "asset": moneda,
        "fiat": "BOB",
        "merchantCheck": False,
        "page": 1,
        "payTypes": [],
        "publisherType": None,
        "rows": 10,
        "tradeType": tipo
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=data)
    ofertas = response.json().get("data", [])
    resultados = []

    for oferta in ofertas:
        adv = oferta["adv"]
        precio = float(adv["price"])
        if (tipo == "BUY" and precio <= max_precio) or (tipo == "SELL" and precio >= max_precio):
            resultados.append({
                "precio": precio,
                "comerciante": oferta["advertiser"]["nickName"],
                "url": f"https://p2p.binance.com/en/advertiserDetail?advertiserNo={oferta['advertiser']['userNo']}"
            })
    return resultados

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{config['telegram_token']}/sendMessage"
    data = {
        "chat_id": config["telegram_user_id"],
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)

while True:
    for moneda in config["monedas"]:
        limites = config["limites"][moneda]
        for tipo, clave in [("BUY", "buy_max"), ("SELL", "sell_min")]:
            ofertas = buscar_ofertas(moneda, tipo, limites[clave])
            for oferta in ofertas:
                msg = f"💱 *{tipo}* oferta de *{moneda}*
💰 Precio: {oferta['precio']} Bs
👤 Usuario: {oferta['comerciante']}
🔗 [Ver oferta]({oferta['url']})"
                enviar_telegram(msg)
    time.sleep(config["intervalo_segundos"])