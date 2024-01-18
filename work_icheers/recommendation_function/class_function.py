import pickle
import json
import pandas as pd
import numpy as np
import datetime
from Sales_Pipeline import pipeline, user_item_matrix
from GenerateRecommendations import WineRecommender

class ProductRecommender:
    def __init__(self, user_id):
        self.user_id = user_id
        self.recommend_products_num = 10
        self.todaymonth = datetime.datetime.now().month
        #self.todayyear = datetime.datetime.now().year
        self.todayyear = 2022
        self.sales_1 = pd.read_excel('/home/r12323007/work_icheers/iCheers/iCheers銷售記錄(2021).xlsx')
        self.sales_2 = pd.read_excel('/home/r12323007/work_icheers/iCheers/iCheers銷售記錄(2022).xlsx')
        self.item = pd.read_excel('/home/r12323007/work_icheers/iCheers/iCheers酒款資料.xlsx')
        self.grape = pd.read_excel('/home/r12323007/work_icheers/iCheers/iCheers品種.xlsx')
        self.users = pd.read_excel('/home/r12323007/work_icheers/iCheers/iCheers客戶資料.xlsx')
        self._prepare_data() # 初始化的時候，一定會跑到這條，一定要先進行資料預處理的動作。

    def _prepare_data(self):
        self.grape = self.grape.groupby('上架編號').agg({'品種': lambda x: '+'.join(list(x))})
        self.sales_1 = pipeline(self.sales_1, self.item, self.grape)
        self.sales_2 = pipeline(self.sales_2, self.item, self.grape)
        self.sales = pd.concat([self.sales_1, self.sales_2], axis=0)

        area = '細區' #目前只能用細區
        criteria = '銷貨數量' #只會影響相似度的計算
        self.UI_mat = user_item_matrix(self.sales, area=area, criteria=criteria)
        self.UI_mat_1 = user_item_matrix(self.sales_1, area=area, criteria=criteria)
        self.UI_mat_2 = user_item_matrix(self.sales_2, area=area, criteria=criteria)

    
    def algorithm1(self):
        # bpr model
        with open('BPR_recommender_細區.pkl', 'rb') as f:
            bpr = pickle.load(f)
        wr = WineRecommender(model=bpr, ui_matirx=self.UI_mat)
        
        with open('group_members.json', 'r') as j:
            group_members = json.load(j)

        recommendations1 = wr.generate_recommendations(user_id=self.user_id, k= self.recommend_products_num, filter=True)
        recommendations1 = [(name, float(score)) for name, score in recommendations1]
        return {"推薦的商品名稱": recommendations1}
    
    def algorithm2(self):
        # 網站歷年熱銷
        wine_totnum = self.sales.groupby("酒款名稱_中文")["銷貨數量"].sum().reset_index().sort_values(by='銷貨數量', ascending=False)
        top_10_products_tot = wine_totnum.head(self.recommend_products_num)
        recommendations2 = top_10_products_tot['酒款名稱_中文'].tolist()
        return {"推薦的商品名稱": recommendations2}

    def algorithm3(self):
        # 本月最熱銷商品
        self.sales['訂單日期'] = pd.to_datetime(self.sales['訂單日期'])
        this_month_data = self.sales[self.sales['訂單日期'].dt.month == self.todaymonth]
        wine_monthnum = this_month_data.groupby("酒款名稱_中文")["銷貨數量"].sum().reset_index().sort_values(by='銷貨數量', ascending=False)
        top_10_products_month = wine_monthnum.head(self.recommend_products_num)
        recommendations3 = top_10_products_month['酒款名稱_中文'].tolist()
        return {"推薦的商品名稱": recommendations3}

    def algorithm4(self):
        # 本年最熱銷商品
        self.sales['訂單日期'] = pd.to_datetime(self.sales['訂單日期'])
        this_year_data = self.sales[self.sales['訂單日期'].dt.year == self.todayyear]
        wine_yearnum = this_year_data.groupby("酒款名稱_中文")["銷貨數量"].sum().reset_index().sort_values(by='銷貨數量', ascending=False)
        top_10_products_year = wine_yearnum.head(self.recommend_products_num)
        recommendations4 = top_10_products_year['酒款名稱_中文'].tolist()
        return {"推薦的商品名稱": recommendations4}

    def algorithm5(self):
        # 這個user的歷年購買數量
        user_wine_totnum = self.sales.groupby(["客戶代碼","酒款名稱_中文"])["銷貨數量"].sum().reset_index().sort_values(by='銷貨數量', ascending=False)
        top_10_products_user_tot = user_wine_totnum.head(self.recommend_products_num)
        recommendations5 = top_10_products_user_tot['酒款名稱_中文'].tolist()
        return {"推薦的商品名稱": recommendations5}
    
    def convert_float32(self, data):
        if isinstance(data, float) and not isinstance(data, float):
            return float(data)
        elif isinstance(data, dict):
            return {k: self.convert_float32(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.convert_float32(x) for x in data]
        return data
    
    # 使用這些內嵌的演算法生成推薦
    def recommend_products(self):
        recommendations = {
            "bpr_model": self.algorithm1(),
            "歷年熱銷商品": self.algorithm2(),
            "本月熱銷商品": self.algorithm3(),
            "本年熱銷商品": self.algorithm4(),
            "這個user的歷年購買": self.algorithm5()
        }
        return recommendations
    
    
    
if __name__ == "__main__":
    user_id_example = '00d0fd357b7a5e18476dec7e46571364'
    recommender = ProductRecommender(user_id_example)
    recommendation_result = recommender.recommend_products()
    print(recommendation_result)