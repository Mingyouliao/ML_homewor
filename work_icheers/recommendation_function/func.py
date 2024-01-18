import pickle
import json
import pandas as pd
import numpy as np
from Sales_Pipeline import pipeline, user_item_matrix
from GenerateRecommendations import WineRecommender

def recommend_products(user_id):
    #讀取資料
    sales_1 = pd.read_excel('/home/r12323007/work_icheers/iCheers/iCheers銷售記錄(2021).xlsx')
    sales_2 = pd.read_excel('/home/r12323007/work_icheers/iCheers/iCheers銷售記錄(2022).xlsx')
    item = pd.read_excel('/home/r12323007/work_icheers/iCheers/iCheers酒款資料.xlsx')
    grape = pd.read_excel('/home/r12323007/work_icheers/iCheers/iCheers品種.xlsx')
    grape = grape.groupby('上架編號').agg({'品種': lambda x: '+'.join(list(x))})
    users = pd.read_excel('/home/r12323007/work_icheers/iCheers/iCheers客戶資料.xlsx')

    #資料處裡
    sales_1 = pipeline(sales_1, item, grape)
    sales_2 = pipeline(sales_2, item, grape)
    sales = pd.concat([sales_1, sales_2], axis=0)
    
    area = '細區' #目前只能用細區
    criteria = '銷貨數量' #只會影響相似度的計算
    #轉為User-Item Matrix
    UI_mat = user_item_matrix(sales, area=area, criteria=criteria)
    UI_mat_1 = user_item_matrix(sales_1, area=area, criteria=criteria)
    UI_mat_2 = user_item_matrix(sales_2, area=area, criteria=criteria)

    def algorithm1(user_id):
        #開啟模型
        with open('BPR_recommender_細區.pkl', 'rb') as f:
            bpr = pickle.load(f)
        wr = WineRecommender(model=bpr, ui_matirx= UI_mat)
        
        with open('group_members.json', 'r') as j:
            group_members = json.load(j)

        #產生推薦清單(filter=True表示過濾掉已消費酒款)
        recommendations1 = wr.generate_recommendations(user_id=user_id, k=10, filter=True)

        return {f"推薦的商品名稱: {recommendations1}"}

    def algorithm2(user_id):
        # 實現演算法 2
        return {"演算法": "Algorithm2", "推薦的商品名稱": ["商品4", "商品5", "商品6"]}

    def algorithm3(user_id):
        # 實現演算法 3
        return {"演算法": "Algorithm3", "推薦的商品名稱": ["商品7", "商品8", "商品9"]}

    def algorithm4(user_id):
        # 實現演算法 4
        return {"演算法": "Algorithm4", "推薦的商品名稱": ["商品10", "商品11", "商品12"]}

    def algorithm5(user_id):
        # 實現演算法 5
        return {"演算法": "Algorithm5", "推薦的商品名稱": ["商品13", "商品14", "商品15"]}

    # 使用這些內嵌的演算法生成推薦
    recommendations = {
        "推薦系統板塊名稱1": algorithm1(user_id),
        "推薦系統板塊名稱2": algorithm2(user_id),
        "推薦系統板塊名稱3": algorithm3(user_id),
        "推薦系統板塊名稱4": algorithm4(user_id),
        "推薦系統板塊名稱5": algorithm5(user_id)
    }

    return recommendations

# 測試函數
if __name__ == "__main__":
    user_id_example = '00d0fd357b7a5e18476dec7e46571364'
    recommendation_result = recommend_products(user_id_example)
    print(recommendation_result)
