# --------------------------------------------------------------------------------------
# 빅데이터 활용 기말평가 과제
# 21903047 정근호

# 라이브러리 불러오기
import datetime
import json
import urllib.request
import json
import re
from konlpy.tag import Okt
from collections import Counter
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from wordcloud import WordCloud

# --------------------------------------------------------------------------------------
# 네이버 블로그 크롤링(코인에 관한 블로그의 데이터들을 수집)
# --------------------------------------------------------------------------------------

# Naver API 설정
client_id = 'hoP0QOt2H8RIwHakQwqe'
client_secret = 'z2K6VlXCmp'


def getRequestUrl(url):
    req = urllib.request.Request(url)
    req.add_header('X-Naver-Client-Id', client_id)
    req.add_header('X-Naver-Client-Secret', client_secret)

    try:
        response = urllib.request.urlopen(req)

        if response.getcode() == 200:
            print('[%s] Url Request Success' % datetime.datetime.now())
            return response.read().decode('utf-8')

    except Exception as e:
        print(e)
        print('[%s] Error for URL : %s' % (datetime.datetime.now(), url))
        return None



def getNaverSearch(node, srcText, start, display):
    base = 'https://openapi.naver.com/v1/search'
    node = '/%s.json' % node  # node: '/blog.json'
    parameters = '?query=%s&start=%s&display=%s' % (urllib.parse.quote(srcText), start, display)

    url = base + node + parameters

    responseDecode = getRequestUrl(url)
    if (responseDecode == None):
        return None
    else:
        return json.loads(responseDecode)


def getPostData(post, jsonResult, cnt):
    title = post['title']
    description = post['description']
    link = post['link']
    postdate = post['postdate']

    jsonResult.append({'cnt': cnt, 'title': title, 'description': description, 'link': link, 'postdate': postdate})
    return


def main():
    # 네이버 블로그 검색을 위해 검색 API 대상을 'blog'로 설정
    node = 'blog'
    # 실행 창에서 검색어를 입력 받아 srcText에 저장
    srcText = input('검색어를 입력하세요 : ')  # '코인' 입력

    cnt = 0
    jsonResult = []

    # getNaverSearch() 함수([CODE 2])를 호출해서
    # start=1 부터 '20'개의 검색 결과를 반환받아 jsonResponse에 저장
    jsonResponse = getNaverSearch(node, srcText, 1, 20)
    total = jsonResponse['total']  # total 전체 검색 결과 개수

    # 검색 결과 jsonResponse에 데이터가 있는 동안 for문 반복 실행
    # for문 안에서 getPostData()([CODE 3])을 반복 실행
    while (jsonResponse != None) and (jsonResponse['display'] != 0):
        for post in jsonResponse['items']:
            cnt += 1
            getPostData(post, jsonResult, cnt)
        if(cnt == 20): # 양이 너무 많아 20개 까지만 데이터를 가져옴
            break

    print('전체 검색 : %d 건' % total)

    # 파일 경로 변경
    with open('/Users/jeong-geunho/PythonProjects/bigdata/%s_naver_%s.json' % (srcText, node), 'w',
              encoding='utf-8') as outfile:
        jsonFile = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)

        outfile.write(jsonFile)

    print('가져온 데이터 : %d 건' % (cnt))
    print('%s_naver_%s.json SAVED' % (srcText, node))


if __name__ == '__main__':
    main()

# --------------------------------------------------------------------------------------
# 텍스트 빈도 분석, 히스토그램, 워드클라우드
# --------------------------------------------------------------------------------------

# 파일 읽기
# json 파일을 읽어서(json.loads()) data 딕셔너리 객체에 저장, 한글이 깨지지 않도록 utf-8 형식으로 인코딩
# json : json 파일을 다루기 위한 모듈
# Okt : 한글 품사 태깅을 위한 모듈
inputFileName = '/Users/jeong-geunho/PythonProjects/bigdata/코인_naver_blog'
data = json.loads(open(inputFileName + '.json', 'r', encoding='utf-8').read())
data

# 분석할 데이터 추출
# 'description' 키의 데이터에서 품사가 명사인 단어만 추출
# 'description' 키의 값(블로그 본문 내용)에서 문자나 숫자가 아닌 것(r'[^\w]')은
# 공백으로 치환해서(re.sub()) 제거하면서 연결해서 전체를 하나의 문자열로 구성
# ＼w : 문자+숫자와 매치, [a-zA-Z0-9_]와 동일한 표현식이다.
message = ''

for item in data:
    if 'description' in item.keys():
        message = message + re.sub(r'[^\w]', ' ', item['description']) + ''

message


# 명사를 추출해서 저장한 message_N에 있는 단어들을 탐색
# 품사 태깅 : 명사 추출
# 품사 태깅 라이브러리인 Okt를 사용해서 명사만 추출해(nlp.nouns()) message_N에 저장
nlp = Okt()
message_N = nlp.nouns(message)
message_N

# Counter() 함수를 사용하여 단어별 출현 횟수를 계산
count = Counter(message_N)
count

# 출현 횟수가 많은 상위 '50'개의 단어 중에서 길이가 1보다 큰 것만 word_count 딕셔너리에 저장하면서 출력하여 확인
word_count = dict()

for tag, counts in count.most_common(50):
    if (len(str(tag)) > 1):
        word_count[tag] = counts
        print("%s : %d" % (tag, counts))

# 히스토그램
# 히스토그램을 그려 단어 빈도를 시각적으로 탐색
# 폰트 경로 변경
font_path = "/Library/Fonts/Arial Unicode.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
matplotlib.rc('font', family=font_name)

plt.figure(figsize=(12, 5))
plt.xlabel('키워드')
plt.ylabel('빈도수')
plt.grid(True)

sorted_Keys = sorted(word_count, key=word_count.get, reverse=True)
sorted_Values = sorted(word_count.values(), reverse=True)

plt.bar(range(len(word_count)), sorted_Values, align='center')
plt.xticks(range(len(word_count)), list(sorted_Keys), rotation=90)

plt.show()

# 워드클라우드 그리기
# 워드클라우드 객체를 생성하고(WordCloud()),
# word_count에서 단어별 빈도수를 계산해서(wc.generate_from_frequencies())
# cloud 객체에 저장하고, 워드클라우드를 생성(plt.imshow())

del word_count['코인'] # '코인'은 검색한 문자이기에 제거

wc = WordCloud(font_path, background_color='ivory',
               width=800, height=600)
cloud = wc.generate_from_frequencies(word_count)

plt.figure(figsize=(8, 8))
plt.imshow(cloud)
plt.axis('off')
plt.show()

# 워드클라우드를 jpg 파일로 저장(to_file())
cloud.to_file(inputFileName + '_cloud.jpg')
