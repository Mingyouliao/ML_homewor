from flask import Flask, jsonify, request, Response
import pandas as pd
import pickle
import json
import datetime
from class_function import ProductRecommender

app = Flask(__name__)

#http://127.0.0.1:5000/recommend?user_id=00d0fd357b7a5e18476dec7e46571364

@app.route('/recommend', methods=['GET'])
def recommend():
    user_id = request.args.get('user_id')
    if user_id:
        recommender = ProductRecommender(user_id)
        recommendation_result = recommender.recommend_products()
        #return jsonify(recommendation_result)
        response = json.dumps(recommendation_result, ensure_ascii=False)
        return Response(response, content_type="application/json; charset=utf-8")
    else:
        return jsonify({"error": "No user_id provided"}), 400
    
if __name__ == '__main__':
    app.run(debug=True)