import os
import sys
import pandas as pd
from elasticsearch_dsl import Document, Text, Keyword, connections

# --- 해결 방법: sys.path에 프로젝트 루트 폴더 추가 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)
# -----------------------------------------------

# 상대 경로 임포트 대신 절대 경로로 수정
from myapp.documents import SilverCareFacilityDocument
# Elasticsearch 서버 연결 설정 (모든 설정을 포함한 최종 코드)
connections.create_connection(
    hosts=['https://localhost:9200'],  # (1) https로 연결
    basic_auth=('elastic', 'oovNYNNQIEHC5ytHKHyR'), # (2) 사용자 이름과 비밀번호로 인증
    verify_certs=False,                 # (3) 인증서 검증을 건너뛰도록 설정
    ssl_show_warn=False,                # (4) 경고 메시지 숨기기
)


# CSV 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_file_path = os.path.join(BASE_DIR, 'myapp', 'static', 'csv', 'output_combined_final.csv')

def index_csv_data():
    """
    CSV 파일을 읽어 Elasticsearch에 데이터를 인덱싱하는 함수
    """
    if not os.path.exists(csv_file_path):
        print(f"오류: {csv_file_path} 파일을 찾을 수 없습니다.")
        return

    try:
        # 인덱스 초기화
        SilverCareFacilityDocument.init()
        try:
            df = pd.read_csv(csv_file_path, encoding='cp949')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_file_path, encoding='utf-8')
        
        df = df.fillna('')

        for _, row in df.iterrows():

            original_address = row.get('주소')
            cleaned_address = original_address # 기본값으로 원본 주소 설정

            if isinstance(original_address, str): # 주소 값이 문자열일 경우에만 처리
                unwanted_text = "인천광역시 동구 요양기관"
                cleaned_address = original_address.replace(unwanted_text, "").strip()

            doc = SilverCareFacilityDocument(
                meta={'id': row.get('시설명', '')},
                facility_name=row.get('시설명', ''),
                institution_type=row.get('기관유형', ''),
                address=cleaned_address,
                phone_number=row.get('전화번호', ''),
                homepage=row.get('홈페이지', ''),
                transportation=row.get('교통편', ''),
                parking_facility=row.get('주차시설', ''),
                designation_date=row.get('장기요양기관지정일', ''),

                capacity=row.get('정원', ),
                current_male=row.get('현원(남)', ),
                current_female=row.get('현원(여)', ),
                waiting_male=row.get('대기(남)', ),
                waiting_female=row.get('대기(여)', ),

                caregiver_type1=row.get('재가노인복지시설방문요양-요양보호사-1급', 0),
                caregiver_type2=row.get('재가노인복지시설방문요양-요양보호사-2급', 0),
                caregiver_suspend=row.get('재가노인복지시설방문요양-요양보호사-유예', 0),
                longterm_caregiver_type1=row.get('재가장기요양기관방문요양-요양보호사-1급', 0),
                longterm_caregiver_type2=row.get('재가장기요양기관방문요양-요양보호사-2급', 0),
                longterm_caregiver_suspend=row.get('재가장기요양기관방문요양-요양보호사-유예', 0),

                nurse=row.get('간호사', 0),
                nursing_assistant=row.get('간호조무사', 0),
                contract=row.get('계약', 0),
                manager=row.get('관리인', 0),
                physical_therapist=row.get('물리치료사', 0),
                assistant=row.get('보조원', 0),
                general_manager=row.get('사무국장', 0),
                office=row.get('사무실', 0),
                office_worker=row.get('사무원', 0),
                social_worker=row.get('사회복지사', 0),
                washing_room=row.get('세면/세탁실', 0),
                head_of_facility=row.get('시설장', 0),
                nutritional_support=row.get('영양사', 0),
                sanitation_worker=row.get('위생원', 0),
                suspended=row.get('유예', 0),
                occupational_therapist=row.get('작업치료사', 0),
                day_night_care=row.get('재가노인복지시설주야간보호', 0),
                cook=row.get('조리원', 0),
                bedrom=row.get('침실', 0),
                toilet=row.get('화장실', 0),
            )
            doc.save()
            
        print("데이터 인덱싱이 성공적으로 완료되었습니다.")

    except Exception as e:
        print(f"데이터 인덱싱 중 오류가 발생했습니다: {e}")

if __name__ == '__main__':
    index_csv_data()