import os
import pandas as pd
from elasticsearch_dsl import Document, Text, Keyword, connections

from myproject.myproject.settings import BASE_DIR

connections.create_connection(hosts=['localhost'])

class Facility(Document):
    name = Text(fields={'raw': Keyword()})
    address = Text()
    phone = Text()
    description = Text()

    class Index:
        name = 'facilities'

    def save(self, **kwargs):
        return super().save(**kwargs)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_file_path = os.path.join(BASE_DIR, 'output_combined_final.csv')

def index_data():

    if not os.path.exists(csv_file_path):
        print(f"CSV file not found: {csv_file_path}")
        return
    
    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8')

        if not Facility.index.exists():
            Facility.init()

        for _,row in df.iterrows():
            facility = Facility(
                name=row.get('시설명', ''),
                address=row.get('소재지도로명주소', ''),
                phone=row.get('전화번호', ''),
                description=row.get('시설설명', '')
            )
            facility.save()

        print("successful")
    
    except Exception as e:
        print("failed")

if __name__ == "__main__":
    index_data()