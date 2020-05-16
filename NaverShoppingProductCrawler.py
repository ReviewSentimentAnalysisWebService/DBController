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

    def getReview(self, soup) : # 댓글의 리뷰를 추출한다 list 반환
        review = []

        for i in range(1, 21):
            try :
                review.append(soup.select("#_review_list > li:nth-child(" + str(i) + ") > div > div.atc")[0].text)
            except IndexError :
                break


        return review

    def getScore(self, soup):  # 리뷰에서 부여한 별점 정보를 가져온다 list 반환
        score = []

        for i in range(1, 21):
            try:
                score.append(soup.select(
                    "#_review_list > li:nth-child(" + str(i) + ") > div > div.avg_area > a > span.curr_avg")[0].text)
            except IndexError:
                break

        return score

    def getDate(self, soup) : # 리뷰를 작성한 날자를 가져온다 list 반환
        date = []
        # _review_list > li:nth-child(" + str(i) +") > div > div.avg_area > span > span:nth-child(3)
        for i in range(1, 21) :
            try :
                date.append(soup.select("#_review_list > li:nth-child(" + str(i) +") > div > div.avg_area > span > span:nth-child(3)")[0].text)
            except IndexError :
                break

        return date
    def setReviewSort(self): # 리뷰 정렬 기준을 날자순으로 변경
        self.driver.find_element_by_css_selector("#_review_sort_select > span:nth-child(2) > a").click() # 날자순
        # self.driver.find_element_by_css_selector("#_review_sort_select > span:nth-child(1) > a").click() # 랭킹순

    def getContent(self, soup) : # 모든 리뷰를 하나의 텍스트로 만들어 주는 함수
        # review = []
        returnStr = ''
        allReview, allScore, allDate = self.getReview(soup), self.getScore(soup), self.getDate(soup)

        for review, score, date in zip(allReview, allScore, allDate) :
            returnStr += review + "\t" + score + "\t" + date + "\n"

        return returnStr


    def getReviewPageCount(self, soup) :
        tempStr = soup.select("#fixed_tab_area > div > ul > li.mall_review > a > em")[0].text.split(",")
        numStr = ""
        for temp in tempStr:
            numStr += temp

        maxReviewCont = int(numStr)  # 총 리뷰의 갯수

        reviewPageCount = int(maxReviewCont / 20) + 1  # 리뷰 페이지의 수

        print("review count complete")
        return reviewPageCount


    def getContext(self, soup) :
        # 먼저 총 리뷰의 갯수를 구해 리뷰 페이지의 수를 구한다
        pageCount = self.getReviewPageCount(soup)

        self.setReviewSort() # 리부 정렬을 날자순으로 바꾼다

        returnStr = "review" + "\t" + "score" + "\t" + "date" + "\n"

        # for i in range(1, pageCount) :
        pageCount = 1 # 한페이지 테스트용
        for i in range( 1, pageCount + 1) :
            self.driver.execute_script("shop.detail.ReviewHandler.page(" + str(i) + ", '_review_paging');")
            time.sleep(0.1)
            response = (self.driver.page_source).encode('utf-8')
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

        response = (self.driver.page_source).encode('utf-8')

        soup = BeautifulSoup(response, 'lxml')

        resultStr = self.getContext(soup)

        # 파일 제목을 결정하는 방법이 필요함 : 현재 nv_mid 값을 사용중
        self.makeTextFile(self.getUrlParsed(URL), resultStr)

        print("crowling complete")

if __name__ == "__main__" :
    crawler = NaverShoppingCrawler()
    crawler.getCrawlling("https://search.shopping.naver.com/detail/detail.nhn?nv_mid=10565213662")