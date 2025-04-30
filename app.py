from flask import Flask, request, jsonify, Response
import requests
import secret

app = Flask(__name__)

@app.route("/api", methods=["GET"])
def api():
    airport = request.args.get("queryAirportTemp")
    stock   = request.args.get("queryStockPrice")
    expr    = request.args.get("queryEval")

    # must have exactly one
    if sum(x is not None for x in (airport, stock, expr)) != 1:
        return Response("Exactly one query parameter must be present.", status=400)

    accept = request.headers.get("Accept", "")
    is_xml = "xml" in accept.lower()

    try:
        if airport:
            result = get_real_temperature(airport)
        elif stock:
            result = get_real_price(stock)
        else:
            result = eval_expression(expr)

        if is_xml:
            return Response(f"<result>{result}</result>",
                            mimetype="application/xml")
        else:
            # jsonify a bare number will emit e.g. 5576.0
            return jsonify(result)

    except Exception as e:
        return Response(f"Internal Server Error: {e}", status=500)


def get_real_temperature(iata_code: str) -> float:
    # 1) Look up the airport to get lat/lon
    url = f"https://iata-airports.p.rapidapi.com/airports/{iata_code.upper()}/"
    headers = {
        "x-rapidapi-key": secret.RAPID_KEY,
        "x-rapidapi-host": "iata-airports.p.rapidapi.com"
    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise Exception(f"Airport lookup failed ({r.status_code}): {r.text}")

    info = r.json()
    lat = info.get("latitude")
    lon = info.get("longitude")
    if lat is None or lon is None:
        raise Exception("Could not find latitude/longitude in airport data")

    # 2) Fetch current weather from Open-Meteo
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }
    w = requests.get(weather_url, params=params)
    if w.status_code != 200:
        raise Exception(f"Weather lookup failed ({w.status_code}): {w.text}")

    cw = w.json().get("current_weather")
    if not cw or "temperature" not in cw:
        raise Exception("No temperature in weather response")

    return float(cw["temperature"])


def get_real_price(stock_symbol):
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-summary"
    headers = {
        "x-rapidapi-key": secret.RAPID_KEY,
        "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }
    params = {"region": "US"}

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        raise Exception(f"API error {resp.status_code}: {resp.text}")

    payload = resp.json()
    # drill down to the array of quote objects
    results = payload.get("marketSummaryAndSparkResponse", {}) \
                     .get("result", [])

    symbol_upper = stock_symbol.upper()
    for item in results:
        # look for any symbol that begins with your query
        if item.get("symbol", "").startswith(symbol_upper):
            # extract the raw numeric price
            price = item.get("regularMarketPrice", {}) \
                        .get("raw", None)
            if price is not None:
                return float(price)
            break

    # if we dropped out without returning
    raise Exception(f"Symbol '{stock_symbol}' not found in market summary")


def eval_expression(expr):
    # very minimal sandbox
    return eval(expr, {"__builtins__": {}})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
