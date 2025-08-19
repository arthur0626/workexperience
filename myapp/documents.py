from elasticsearch_dsl import Document, Text, Keyword, Integer, connections

connections.create_connection(
    hosts=['https://localhost:9200'],
    basic_auth=('elastic', 'oovNYNNQIEHC5ytHKHyR'),
    verify_certs=False,
    ssl_show_warn=False,
)

class SilverCareFacilityDocument(Document):
    facility_name = Text(analyzer='nori')
    institution_type = Text()
    address = Text(analyzer='nori')
    phone_number = Keyword()
    homepage = Keyword()
    transportation = Text()
    parking_facility = Text()
    designation_date = Text()

    capacity = Text()
    current_male = Text()
    current_female = Text()
    waiting_male = Text()
    waiting_female = Text()

    caregiver_type1 = Text()
    caregiver_type2 = Text()
    caregiver_suspended = Text()
    longterm_caregiver_type1 = Text()
    longterm_caregiver_type2 = Text()
    longterm_caregiver_suspended = Text()

    nurse = Text()
    nursing_assistant = Text()
    contract = Text()
    manager = Text()
    physical_therapist = Text()
    assistant = Text()
    general_manager = Text()
    office = Text()
    office_worker = Text()
    social_worker = Text()
    washing_room = Text()
    head_of_facility = Text()
    nutritionist = Text()
    sanitation_worker = Text()
    suspended = Text()
    occupational_therapist = Text()
    day_night_care = Text()
    cook = Text()
    bedroom = Text()
    toilet = Text()

    class Index:
        name = 'silvercare_facilities'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'nori': {
                        'tokenizer': 'nori_tokenizer'
                    }
                }
            }
        }