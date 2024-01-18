def pipeline(sales, item, grape):
    #合併銷售資料、酒款資料和品種資料
    sales = sales.merge(item.drop(columns='容量'),  how='left', on='上架編號',indicator=False)
    sales = sales.merge(grape,  how='left', on='上架編號' ,indicator=False)
    sales = sales[sales['訂單狀態'] == '已完成']

    #刪除產區1為空的資料
    sales.dropna(subset=['產區1'], inplace=True)

    #保留葡萄酒資料
    sales = sales[sales['商品類型'] == '葡萄酒']

    #篩掉不重要資料
    sales = sales[sales['類型'].isin(['氣泡葡萄酒', '葡萄酒', '加烈葡萄酒'])]

    #填補產區2及顏色區缺失值
    sales[['產區2','產區3','產區4','顏色']] = sales[['產區2','產區3','產區4','顏色']].fillna(' ')

    sales['大區'] = sales['產區1'] + sales['產區2'] + sales['顏色']

    sales['細區'] = sales['產區1'] + sales['產區2'] + sales['產區3'] + sales['顏色']

    sales['超細區'] = sales['產區1'] + sales['產區2'] + sales['產區3'] + sales['產區4'] + sales['顏色']

    sales['大區+品種'] = sales['產區1'] + sales['產區2'] + sales['品種'] + sales['顏色']

    sales['細區+品種'] = sales['產區1'] + sales['產區2'] + sales['產區3'] + sales['品種'] + sales['顏色']

    def price_interval(price):
        if price<=500:
            return '$500以下'
        elif (price>500)&(price<=1000):
            return '$501-1000'
        elif (price>1000)&(price<=2000):
            return '$1001-2000'
        elif (price>2000)&(price<=3000):
            return '$2001-3000'
        elif (price>3000)&(price<=4000):
            return '$3001-4000'
        elif (price>4000)&(price<=5000):
            return '$4001-5000'
        elif (price>5000)&(price<=10000):
            return '$5001-10000'
        elif (price>10000)&(price<=20000):
            return '$10001-20000'
        else:
            return '$20000以上'

    sales['單價區間'] = sales['銷售單價'].apply(price_interval)

    return sales


def user_item_matrix(sales, area, criteria):
    sales = sales.groupby(['客戶代碼', area])[criteria].sum().unstack().fillna(0)
    return sales