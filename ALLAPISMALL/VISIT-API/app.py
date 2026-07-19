from flask import Flask, jsonify
import aiohttp
import asyncio
import requests

from byte import *
from protobuf_parser import Parser, Utils

app = Flask(__name__)

# =========================
# جلب التوكن من API
# =========================
def fetch_tokens(uid, password):
    url = "https://amin-king-free.vercel.app/token"
    params = {
        "uid": uid,
        "password": password
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("🔹 API Response:", data)

            if data.get("status") == "success" and "token" in data:
                return [data["token"]]  # نرجعه كـ list
            else:
                print("⚠️ فشل جلب التوكن")
                return []
        else:
            print(f"⚠️ HTTP Error: {response.status_code}")
            return []

    except Exception as e:
        print(f"⚠️ Exception: {e}")
        return []

# =========================
# إرسال طلب واحد
# =========================
async def visit(session, token, uid, data):
    url = "https://clientbp.ggblueshark.com/GetPlayerPersonalShow"
    headers = {
        "ReleaseVersion": "OB48",
        "X-GA": "v1 1",
        "Authorization": f"Bearer {token}",
        "Host": "clientbp.ggblueshark.com",
        "Content-Type": "application/octet-stream"
    }

    try:
        async with session.post(url, headers=headers, data=data, ssl=False):
            pass
    except:
        pass

# =========================
# إرسال الطلبات بشكل متوازي
# =========================
async def send_requests_concurrently(tokens, uid, num_requests):
    connector = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=connector) as session:
        payload = bytes.fromhex(
            encrypt_api("08" + Encrypt_ID(uid) + "1801")
        )

        tasks = [
            asyncio.create_task(
                visit(session, tokens[i % len(tokens)], uid, payload)
            )
            for i in range(num_requests)
        ]

        await asyncio.gather(*tasks)

# =========================
# API Endpoint
# =========================
@app.route('/<int:uid>', methods=['GET'])
def send_visits(uid):
    PASSWORD = "PASSWORD_HERE"  # ← ضع الباسورد هنا

    tokens = fetch_tokens(uid, PASSWORD)

    if not tokens:
        return jsonify({"message": "❌ No valid token found"}), 500

    num_requests = 1000
    asyncio.run(send_requests_concurrently(tokens, uid, num_requests))

    return jsonify({
        "status": "success",
        "uid": uid,
        "visits_sent": num_requests,
        "tokens_used": len(tokens)
    }), 200

# =========================
# تشغيل السيرفر
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1088, debug=False)