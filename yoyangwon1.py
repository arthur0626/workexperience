import time, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

options=Options()
options.add_experimental_option('detach',True)
options.add_experimental_option('excludeSwitches',['enable-logging'])

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

my_url = "https://www.silvercarekorea.com/silver/list.php?pagenum=4&addcode=28140&searchkeyword=&orderby=&hashtag=&gubun="
driver.get(my_url)

time.sleep(2)

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
table = soup.select_one('table.datatable12')

results = []
if table:
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all(['td', 'th'])
        row_data = [col.get_text(strip=True) for col in cols]
        # (필요하다면 첫 번째 tr은 헤더니까 제외 등 가공 가능)
        if row_data:  # 빈 행 제외
            results.append(row_data)

for row in results:
    print(row)

address_keyword = "인천광역시"
dong_ends = ["동", "가", "읍", "면"]

def smart_split(text):
    # 인천광역시 위치 탐색
    idx_start = text.find(address_keyword)
    if idx_start == -1:
        # 패턴 없으면 전체를 기타정보로
        return text, "", ""
    name = text[:idx_start].strip()
    rest = text[idx_start:].strip()
    # '동', '가', '읍', '면' 중 가장 먼저 등장하는 위치 찾기
    dong_idx = -1
    for end in dong_ends:
        idx = rest.find(end)
        if idx != -1:
            # +1도 반드시 포함(예: 송현동까지 주소로)
            dong_idx = idx + 1
            break
    if dong_idx == -1:
        # 못 찾으면 전체를 주소로
        return name, rest, ""
    addr = rest[:dong_idx]
    etc = rest[dong_idx:].strip(" /")  # 불필요한 /, 공백 제거
    return name, addr, etc

# 적용 예시
for i, row in enumerate(results):
    if i == 0:  # 헤더스킵(첫 줄)
        continue
    text = row[1]  # 요양원명+주소+기타한 셀
    name, addr, etc = smart_split(text)
    print(f"시설명: {name} | 주소: {addr} | 기타정보: {etc}")

try:
    driver.quit()
except:
    pass

# 🚨 안전한 WebDriver 초기화
def create_driver():
    options = Options()
    # headless 제거해서 브라우저 창 보면서 디버깅
    options.add_experimental_option('detach', True)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# 새 드라이버 생성
driver = create_driver()

# 간단한 테스트부터
print("=== WebDriver 테스트 ===")
try:
    test_url = 'https://www.silvercarekorea.com/silver/list.php?pagenum=1&addcode=28140&searchkeyword=&orderby=&hashtag=&gubun='
    driver.get(test_url)
    print("✅ 페이지 로딩 성공!")
    
    time.sleep(3)
    
    # 페이지 소스 확인
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print(f"✅ 페이지 파싱 성공! HTML 길이: {len(soup.get_text())}")
    
    # 테이블 찾기
    all_tables = soup.find_all('table')
    print(f"✅ 테이블 개수: {len(all_tables)}")
    
    # 요양원 텍스트 찾기
    yoyangwon_texts = soup.find_all(text=lambda text: text and '요양원' in text)
    print(f"✅ '요양원' 포함 텍스트: {len(yoyangwon_texts)}개")
    
    if len(yoyangwon_texts) > 0:
        print("처음 3개 요양원:")
        for i, text in enumerate(yoyangwon_texts[:3]):
            clean_text = text.strip()
            if len(clean_text) > 5:
                print(f"  {i+1}. {clean_text}")
    
except Exception as e:
    print(f"❌ 에러 발생: {e}")

# 테스트 완료 후 브라우저는 열어둠 (detach=True 때문에)
print("\n=== 테스트 완료 ===")
print("브라우저 창에서 페이지가 제대로 로딩되었는지 직접 확인해보세요!")
print("확인 후 다음 단계 진행 가능합니다.")

# 드라이버 생성
options = Options()
options.add_experimental_option('detach', True)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 1페이지만 테스트
url = 'https://www.silvercarekorea.com/silver/list.php?pagenum=1&addcode=28140&searchkeyword=&orderby=&hashtag=&gubun='
driver.get(url)
time.sleep(3)

soup = BeautifulSoup(driver.page_source, 'html.parser')

# 테이블과 링크 확인
all_tables = soup.find_all('table')
print(f"테이블 개수: {len(all_tables)}")

if len(all_tables) > 0:
    table = all_tables[0]  # 첫 번째 테이블
    rows = table.find_all('tr')
    print(f"행 개수: {len(rows)}")
    
    # 링크가 있는지 확인
    links = table.find_all('a')
    print(f"테이블 내 링크 개수: {len(links)}")
    
    if len(links) > 0:
        print("✅ 링크 찾음! 전체 코드 실행 가능")
        for i, link in enumerate(links[:3]):
            print(f"  {i+1}. {link.get_text()[:20]} → {link.get('href', 'href없음')}")
    else:
        print("❌ 링크 없음. 구조 분석 필요")
else:
    print("❌ 테이블 없음. 페이지 구조 확인 필요")

try:
    driver.get('https://www.silvercarekorea.com/silver/list.php?pagenum=1&addcode=28140')
    time.sleep(2)
    # ... (크롤링 코드)
except Exception as e:
    print(f"에러: {e}")
finally:
    driver.quit()


time.sleep(2)


# ... (Selenium 등 세팅 코드)

for row in table.find_all('tr')[1:]:
    cols = row.find_all('td')
    if len(cols) < 2:
        continue
    a_tag = cols[1].find('a')
    # 반드시 'detail.php'만 포함한 링크만!
    if a_tag and a_tag.get('href') and 'detail.php' in a_tag.get('href'):
        detail_url = a_tag['href']
        if not detail_url.startswith('http'):
            if not detail_url.startswith('/'):
                detail_url = '/' + detail_url
            detail_url = 'https://www.silvercarekorea.com' + detail_url
        # 이하 상세페이지 접근 & 주소 추출은 기존 로직과 동일하게 실행


options = Options()
options.add_argument('--headless') # (필요시 창 안띄움, 안해도 됨)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 크롤링할 URL 리스트
urls = [
    "https://www.silvercarekorea.com/silver/detail.php?uid=6602",
    "https://www.silvercarekorea.com/silver/detail.php?uid=40641",
    "https://www.silvercarekorea.com/silver/detail.php?uid=40640"
    # 여기에 필요한 링크 추가 가능
]

headers = {"User-Agent": "Mozilla/5.0"}

def get_value(soup, label):
    for td in soup.find_all('td'):
        td_text = td.get_text(" ", strip=True)
        if td_text.replace(" ", "").startswith(label):
            next_td = td.find_next_sibling('td')
            if next_td:
                return next_td.get_text(strip=True)
            else:
                return td_text.replace(label, "").strip(" :")
    return ""

for i, url in enumerate(urls, 1):
    print(f"\n{'='*15} 링크 {i} 정보 ({url}) {'='*15}")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()  # 요청 실패 시 예외 발생
        soup = BeautifulSoup(resp.content, 'html.parser')

        기관유형 = get_value(soup, "기관유형")
        주소 = get_value(soup, "주소")
        전화번호 = get_value(soup, "전화번호")
        홈페이지 = get_value(soup, "홈페이지")
        장기요양기관지정일 = get_value(soup, "장기요양기관지정일")
        교통편 = get_value(soup, "교통편")
        주차시설 = get_value(soup, "주차시설")

        print(f"기관유형: {기관유형}")
        print(f"주소: {주소}")
        print(f"전화번호: {전화번호}")
        print(f"홈페이지: {홈페이지}")
        print(f"장기요양기관지정일: {장기요양기관지정일}")
        print(f"교통편: {교통편}")
        print(f"주차시설: {주차시설}")
    except requests.RequestException as e:
        print(f"링크 {i} 요청 중 오류 발생: {e}")

from selenium import webdriver
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome()  # 크롬드라이버 필요
driver.get('https://www.silvercarekorea.com/silver/detail.php?uid=40640')            # 타겟 URL
time.sleep(2)                # 렌더링 기다리기

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
table = soup.find('table', {'class': 'datatable'})
# 이하 동일하게 rows 등 처리
driver.quit()

tables = soup.find_all('table', class_='datatable')

# 인덱스 3, 4, 5 세 개의 표를 순서대로 처리
for idx in [3, 4, 5]:
    #print(f"Table at index {idx}:")
    employee_table = tables[idx]

    rows = employee_table.find_all('tr')
    data = []
    for tr in rows:
        cells = tr.find_all('td')
        row = []
        for td in cells:
            spans = td.find_all('span')
            if spans:
                text = ' '.join([span.get_text(strip=True) for span in spans])
            else:
                text = td.get_text(strip=True)
            row.append(text)
        if row:
            data.append(row)

    for row in data:
        print(row)
    print("\n")  # 표별로 구분을 위해 빈 줄 추가