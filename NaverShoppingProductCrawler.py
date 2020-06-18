import pymysql.cursors

# from review_preprocessor import ReviewPreprocessor
# from sentiment_analyzer import SentimentAnalyzer


# from selenium.common.exceptions import NoSuchElementException
# from NaverShoppingProductsCrawler import NaverShoppingProductsCrawler
# from NaverShoppingReviewCrawler import NaverShoppingReviewCrawler

# Connect to the database

class sentimentalDBM:
    connection = None

    def __init__(self):

        self.connection = pymysql.connect(host='127.0.0.1',
                                          user='root',
                                          password='mysql',
                                          db='testsentimental',  # Schema 선택
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def __del__(self):
        self.connection.close()

    def insertProduct(self, nv_mids, names, prices, dates, img_urls, cat_id):
        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `product_list`(`nv_mid`, `cat_id`, `name`, `date`, `img_url`, `price`) VALUES(%s, %s, %s, %s, %s, %s);"
                for nv_midTmp, namesTmp, pricesTmp, dateTmp, img_urlTmp in zip(nv_mids, names, prices, dates, img_urls):
                    try:
                        cursor.execute(sql, (nv_midTmp, cat_id, namesTmp, dateTmp, img_urlTmp, pricesTmp))
                    except pymysql.err.IntegrityError as e:
                        print(e)

            self.connection.commit()
        finally:
            print("insertProduct Complete")

    def selectProduct(self, cat_id, limit=None):
        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                if limit is None:
                    sql = "SELECT nv_mid FROM product_list WHERE cat_id=%s;"
                else:
                    sql = "SELECT nv_mid FROM product_list WHERE cat_id=%s limit " + str(limit) + ";"
                cursor.execute(sql, cat_id)
                rows = cursor.fetchall()
                return rows
        finally:
            print("ACTION Complete")

    def insertReivew(self, review, score, date, nv_mid):
        # Connect to the database
        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                "INSERT INTO `product_review`(`nv_mid`, `review`, `score`, `date`) VALUES('1', '1', '1', '1', '1');"
                sql = "INSERT INTO `product_review`(`nv_mid`, `review`, `score`, `date`) VALUES(%s, %s, %s, %s);"
                for reviewTmp, scoreTmp, dateTmp in zip(review, score, date):
                    try:
                        cursor.execute(sql, (nv_mid, reviewTmp, scoreTmp, dateTmp))
                    except pymysql.err.IntegrityError:
                        print("중복 발생 pass")

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()
        finally:
            print("ACTION Complete")

    def selectReview(self, nv_mid, limit=None):
        # Connect to the database

        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                if limit is None:
                    sql = "SELECT review_id, review FROM product_review WHERE nv_mid=%s;"
                else:
                    sql = "SELECT review_id, review FROM product_review WHERE nv_mid=%s limit " + str(limit) + ";"
                cursor.execute(sql, nv_mid)
                rows = cursor.fetchall()
                return rows
        finally:
            print("ACTION Complete")

    def selectCategorys(self):
        # Connect to the database

        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "SELECT * FROM category;"
                cursor.execute(sql)
                rows = cursor.fetchall()
                return rows
        finally:
            print("ACTION Complete")

    def selectKeywords(self, cat_id):
        # Connect to the database
        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "SELECT key_id, keyword FROM keyword WHERE cat_id=%s;"
                cursor.execute(sql, cat_id)
                rows = cursor.fetchall()
                return_list = []
                for result in rows:
                    return_list.append(result['keyword'])

                # return return_list
                return rows
        finally:
            print("ACTION Complete")

    def insertReviewSentimental(self, nv_mid, review_id, keywords, results, senti_scores):
        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `product_review_sentimental` (`nv_mid`, `review_id`, `sentence_number`, `key_id`, `sentence`, `senti_score`, `quality_score`) VALUES (%s, %s, %s, %s, %s, %s, %s);"
                sentence_number = 0
                for result, senti_score in zip(results, senti_scores):
                    # result struct : ['sentence', keyword ,senti_score(0~1사이), quality_score]
                    sentence_number += 1
                    key_id = next(item["key_id"] for item in keywords if item["keyword"] == result[1])
                    try:
                        cursor.execute(sql, (nv_mid, int(review_id), sentence_number, int(key_id),
                                             result[0], senti_score, result[2]))
                    except pymysql.err.IntegrityError:
                        print("중복 발생 pass")

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()
        finally:
            print("ACTION Complete")


"""
def crawllingProducts(cat_id,  pagecount = None):
    crawler = NaverShoppingProductsCrawler.ProductCrawler()
    return crawler.getCrawlling(cat_id, pagecount)

def crawlingAllProducts():
    # cat_ids = "50000151",  "50000437", "50000438", "50001203"
    dbms = sentimentalDBM()
    cat_ids = dbms.selectCategorys()
    print(cat_ids)
    for cat_id in cat_ids:
        print(cat_id)
        nv_mids, names, prices, dates, img_urls = crawllingProducts(cat_id['cat_id'], 10)
        # print(nv_mids, names, prices, dates, img_urls )
        dbms.insertProduct(nv_mids, names, prices, dates, img_urls, cat_id['cat_id'])

def crawlingReviews(cat_id = None):
    crawler = NaverShoppingReviewCrawler.ReviewCrawler()
    dbms = sentimentalDBM()

    nv_mids = dbms.selectProduct(cat_id)

    for nv_mid in nv_mids:
        nv_mid = nv_mid['nv_mid']
        try:
            reviews, scores, dates = crawler.getCrawlling(nv_mid)
        except NoSuchElementException as e:
            print(e)
        # 중복 제거
        set_list = list(set(zip(reviews, scores, dates)))
        reviews, scores, dates = map(list, zip(*set_list))
        # 중복 제거 완료
        dbms.insertReivew(reviews, scores, dates, nv_mid)

def crawlingAllReview():
    dbms = sentimentalDBM()
    cat_ids = dbms.selectCategorys()
    print(cat_ids)
    for cat_id in cat_ids:
        cat_id = cat_id['cat_id']
        crawlingReviews(cat_id)
"""


def sentimentalProcessor():
    dbms = sentimentalDBM()
    cat_ids = dbms.selectCategorys()
    cat_id = cat_ids[3]["cat_id"]

    keywords = dbms.selectKeywords(cat_id)
    products = dbms.selectProduct(cat_id, limit=10)

    keywords_str = []  # 모델 삽입용

    senti_scores = []

    sent_analyzer = SentimentAnalyzer()

    for keyword in keywords:
        if keyword["keyword"] != "기타":
            keywords_str.append(keyword["keyword"])

    for product in products:
        reviews = dbms.selectReview(product["nv_mid"], limit=100)

        processor = ReviewPreprocessor("w2vmodel_mouse", keywords_str)
        for review in reviews:
            results = processor.process(review['review'])
            for result in results:
                print(result[0])
                senti_scores.append(sent_analyzer.analyze(result[0]))

            dbms.insertReviewSentimental(product["nv_mid"], review["review_id"], keywords, results, senti_scores)


if __name__ == "__main__":
    sentimentalProcessor()
