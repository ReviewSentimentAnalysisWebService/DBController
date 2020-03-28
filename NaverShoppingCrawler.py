from bs4 import BeautifulSoup
from selenium import webdriver
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

    def getScore(self, soup) : # 리뷰에서 부여한 별점 정보를 가져온다 list 반환
        score = []

        for i in range(1, 21) :
            try :
                score.append(soup.select("#_review_list > li:nth-child(" + str(i) +") > div > div.avg_area > a > span.curr_avg")[0].text)
            except IndexError :
                break

        return score

    def getContent(self, soup) : # 모든 리뷰를 하나의 텍스트로 만들어 주는 함수
        # review = []
        returnStr = ''
        allReview, allScore = self.getReview(soup), self.getScore(soup)

        for review,  score in zip(allReview, allScore) :
            returnStr += review + "\t" + score + "\n"

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

        returnStr = "review" + "\t" + "score" + "\n"

        # for i in range(1, pageCount) :
        # pageCount = 1 # 한페이지 테스트용
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
    def getCrawlling(self, URL):
        self.driver.get(URL)

        response = (self.driver.page_source).encode('utf-8')

        soup = BeautifulSoup(response, 'lxml')

        resultStr = self.getContext(soup)

        # 파일 제목을 결정하는 방법이 필요함 : 현재 nv_mid 값을 사용중
        self.makeTextFile(URL.split("=").pop(), resultStr)

        print("crowling complete")