from flask import Flask, request, jsonify, Response
import json
import requests

app = Flask(__name__)
#http://127.0.0.1:8080/recommend?user_id=00d0fd357b7a5e18476dec7e46571364

def get_recommendation_from_original_api(user_id):
    url = f"http://127.0.0.1:5000/recommend?user_id={user_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # 假設回應是JSON格式
    else:
        return None

@app.route('/get_recommendation', methods=['GET'])
def get_recommendation():
    user_id = "00d0fd357b7a5e18476dec7e46571364"
    if user_id:
        data = get_recommendation_from_original_api(user_id)
        response = json.dumps(data, ensure_ascii=False)
        if data:
            return Response(response, content_type="application/json; charset=utf-8")
        else:
            return jsonify({"error": "無法獲取推薦數據"}), 404
    else:
        return jsonify({"error": "未提供user_id"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8080)  # 您可以選擇不同的端口以避免衝突

