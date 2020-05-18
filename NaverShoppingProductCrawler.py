from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import  urlparse
import time


class NaverShoppingCrawler :
    driver = None

    def __init__(self):

        self.driver = webdriver.Chrome("chromedriver")
        self.driver.implicitly_wait(1)

    def __del__(self):
        self.driver.close()

    def getReviewList(self, soup):
        return soup.find_all(class_="thumb_nail")

    def getReview(self, soup) : # 댓글의 리뷰를 추출한다 list 반환
        reviews = []

        for review in soup :
            reviews.append(review.find(class_="atc").text)

        return reviews

    def getScore(self, soup):  # 리뷰에서 부여한 별점 정보를 가져온다 list 반환
        scores = []

        for score in soup :
            scores.append(score.find(class_="curr_avg").text)

        return scores

    def getDate(self, soup) : # 리뷰를 작성한 날자를 가져온다 list 반환
        dates = []

        for date in soup :
            dates.append(date.find_all(class_="info_cell")[2].text)

        return dates

    def setReviewSort(self): # 리뷰 정렬 기준을 날자순으로 변경
        self.driver.find_element_by_css_selector("#_review_sort_select > span:nth-child(2) > a").click() # 날자순
        # self.driver.find_element_by_css_selector("#_review_sort_select > span:nth-child(1) > a").click() # 랭킹순

    def getReviewPageCount(self, soup) :
        reviewPages = soup.select("#_review_paging > a.next_end")[0]['onclick'].split("(")[1].split(',')[0]
        return reviewPages

    def getContent(self, soup) : # 모든 리뷰를 하나의 텍스트로 만들어 주는 함수

        reviewDivs = self.getReviewList(soup)
        # review = []
        returnStr = ''

        allReview = self.getReview(reviewDivs)
        allScore = self.getScore(reviewDivs)
        allDate = self.getDate(reviewDivs)

        for review, score, date in zip(allReview, allScore, allDate) :
            returnStr += review + "\t" + score + "\t" + date + "\n"

        return returnStr


    def getContext(self) :

        self.setReviewSort() # 리뷰 정렬을 날자순으로 바꾼다
        time.sleep(1)

        response = self.driver.page_source.encode('utf-8')
        soup = BeautifulSoup(response, 'lxml')

        pageCount = self.getReviewPageCount(soup)

        returnStr = "review" + "\t" + "score" + "\t" + "date" + "\n"

        # for i in range(1, pageCount) :
        pageCount = 10
        for i in range( 1, pageCount + 1) :
            self.driver.execute_script("shop.detail.ReviewHandler.page(" + str(i) + ", '_review_paging');")
            time.sleep(1)

            response = self.driver.page_source.encode('utf-8')
            soup = BeautifulSoup(response, 'lxml')

            returnStr += self.getContent(soup)

            print(str(i) + "/" + str(pageCount) +  "page crowling complete")

        print("Total " + str(pageCount) + "pages crowling complete")

        return returnStr


    def makeTextFile(self, fileName, resultString):
        txt = fileName + ".txt"
        f = open(txt, 'w', encoding='utf-8')

        f.write(resultString)

        f.close()

        print("File save complete : " + txt)
        # test

    def getUrlParsed(self, URL):
        url = urlparse(URL)
        return url.query.split("&")[0].split("=")[1]  # nvMid 값을 추출함

    def getCrawlling(self, URL):
        self.driver.get(URL)

        resultStr = self.getContext()
        # 파일 제목을 결정하는 방법이 필요함 : 현재 nv_mid 값을 사용중
        self.makeTextFile(self.getUrlParsed(URL), resultStr)

        print("crowling complete")

if __name__ == "__main__" :
    crawler = NaverShoppingCrawler()
    crawler.getCrawlling("https://search.shopping.naver.com/detail/detail.nhn?nv_mid=10565213662")