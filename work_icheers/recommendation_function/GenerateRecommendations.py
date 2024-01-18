import pandas as pd
import numpy as np

class WineRecommender:

    def __init__(self, model, ui_matirx):
        self.model = model
        self.ui_matrix = ui_matirx
        self.u_map = dict(zip(self.ui_matrix.index, range(self.ui_matrix.shape[0])))
        self.i_map = dict(enumerate(self.ui_matrix.columns))

    #===============================================================================================================================
    #推薦測試函數
    def generate_recommendations_test(self, user_id, train_data, k=10):
        #預測該客戶對商品的置信度分數
        user_num = self.u_map[user_id]
        recommendations = self.model.recommend(user_num, train_data[user_num], N=k, filter_already_liked_items=True)

        recommendations_lst = []
        for id, score in zip(recommendations[0], recommendations[1]):
            item_name = self.i_map.get(id, f'Item {id}')
            recommendations_lst.append((item_name, score))

        return recommendations_lst
    #===============================================================================================================================
    #推薦生成函數(針對現有客戶)
    def generate_recommendations(self, user_id, k=10, filter=True):
        #該顧客的消費紀錄
        user_record = self.ui_matrix.loc[user_id]
        #預測該客戶對商品的置信度分數
        user_num = self.u_map[user_id]
        user_vector = self.model.user_factors[user_num]
        scores = self.model.item_factors.dot(user_vector)
        top_item_indices = scores.argsort()[:][::-1]

        #篩選出客戶還沒買過的酒款中分數前k名的酒款
        recommendations = []
        for item_index in top_item_indices:
            item_name = self.i_map.get(item_index, f'Item {item_index}')
            if filter == True:
                if user_record[item_name] <= 0:
                    recommendations.append((item_name, scores[item_index]))
            else:
                recommendations.append((item_name, scores[item_index]))

            if len(recommendations) == k:
                    break

        return recommendations
    #===============================================================================================================================
    #推薦生成函數(針對虛擬客戶)
    def generate_recommendations_for_virtual_user(self, sales_record=None, n=5, k=10):
        #確認消費紀錄符合格式
        if sales_record.shape != (len(self.i_map),):
            raise ValueError(f"The sales record must be a 1*{len(self.i_map)} numpy array.")

        #計算與其他客戶的餘弦相似度，並取相似度前n高的客戶
        top_n_similarity = (
            self.ui_matrix.dot(sales_record)/
            (np.sqrt(np.square(self.ui_matrix).sum(axis=1))*np.sqrt(np.square(sales_record).sum()))
            ).sort_values(ascending=False)[:n]

        #依照相似度對用戶因子進行加權平均來得到虛擬用戶的因子
        sim_users_id = top_n_similarity.index.map(self.u_map)
        sim_users_factors = self.model.user_factors[sim_users_id]
        virtual_user_factors = top_n_similarity.dot(sim_users_factors)/sum(top_n_similarity)

        #計算分數並取分數前k高的酒款
        scores = self.model.item_factors.dot(virtual_user_factors)
        top_item_indices = scores.argsort()[-k:][::-1]

        #列出推薦清單
        recommendations = []
        for item_index in top_item_indices:
            item_name = self.i_map.get(item_index, f'Item {item_index}')
            recommendations.append((item_name, scores[item_index]))

        return recommendations