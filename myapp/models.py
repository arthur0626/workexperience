from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

def validate_korean_only(value):
    # 정규 표현식을 사용하여 값이 한글과 공백으로만 구성되어 있는지 확인합니다.
    if not re.fullmatch(r'^[가-힣\s]+$', value):
        raise ValidationError('이름은 한글만 입력 가능합니다.')
    
class ProtectedProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='protected_profile')
    number = models.PositiveIntegerField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=False, null=False, validators=[validate_korean_only])
    age = models.PositiveIntegerField(blank=False, null=False)
    sex = models.CharField(choices=[('남', '남'), ('여', '여')], default='남')
    guardian = models.CharField(choices=[('유', '유'), ('무', '무')], default='무')
    address = models.TextField(blank=True, null=True)
    address_detail = models.TextField(blank=True, null=True)
    budget_min = models.PositiveBigIntegerField(blank=True, null=True)
    budget_max = models.PositiveBigIntegerField(blank=True, null=True)
    preferred_services = models.TextField(blank=True, null=True)
    health_conditions = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} (피보호자)"
    
    def save(self, *args, **kwargs):
        # 새로운 객체이거나 number가 아직 할당되지 않은 경우
        if self._state.adding and self.number is None:
            # 현재 사용자의 가장 큰 'number' 값을 찾습니다.
            # 쿼리셋이 비어있을 경우 max_number는 None이 됩니다.
            max_number = ProtectedProfile.objects.filter(user=self.user).aggregate(models.Max('number'))['number__max']

            # 만약 기존 프로필이 없다면 1부터 시작하고, 있다면 최대값에 1을 더합니다.
            self.number = (max_number or 0) + 1
        super().save(*args, **kwargs)

class SelfProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='self_profile')
    kakao_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    scrapped = models.BooleanField(default=False)
    recent = models.BooleanField(default=False)
    reviews = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} (자신)"

from django.db import models

class SilverCareFacility(models.Model):
    # 기본 정보
    facility_name = models.CharField(max_length=200, verbose_name="시설명")
    institution_type = models.CharField(max_length=100, verbose_name="기관유형")
    address = models.CharField(max_length=255, verbose_name="주소")
    phone_number = models.CharField(max_length=20, verbose_name="전화번호", blank=True, null=True)
    homepage = models.URLField(verbose_name="홈페이지", blank=True, null=True)
    designation_date = models.DateField(verbose_name="장기요양기관지정일", blank=True, null=True)
    transportation = models.CharField(max_length=255, verbose_name="교통편", blank=True, null=True)
    parking_facility = models.CharField(max_length=100, verbose_name="주차시설", blank=True, null=True)

    # 인원 정보
    capacity = models.IntegerField(default=0, verbose_name="정원")
    current_male = models.IntegerField(default=0, verbose_name="현원(남)")
    current_female = models.IntegerField(default=0, verbose_name="현원(여)")
    waiting_male = models.IntegerField(default=0, verbose_name="대기(남)")
    waiting_female = models.IntegerField(default=0, verbose_name="대기(여)")

    # 요양보호사 및 직원 정보
    caregiver_type1 = models.IntegerField(default=0, verbose_name="재가노인복지시설방문요양-요양보호사-1급")
    caregiver_type2 = models.IntegerField(default=0, verbose_name="재가노인복지시설방문요양-요양보호사-2급")
    caregiver_suspended = models.IntegerField(default=0, verbose_name="재가노인복지시설방문요양-요양보호사-유예")
    longterm_caregiver_type1 = models.IntegerField(default=0, verbose_name="재가장기요양기관방문요양-요양보호사-1급")
    longterm_caregiver_type2 = models.IntegerField(default=0, verbose_name="재가장기요양기관방문요양-요양보호사-2급")
    longterm_caregiver_suspended = models.IntegerField(default=0, verbose_name="재가장기요양기관방문요양-요양보호사-유예")

    nurse = models.IntegerField(default=0, verbose_name="간호사")
    nursing_assistant = models.IntegerField(default=0, verbose_name="간호조무사")
    contract = models.IntegerField(default=0, verbose_name="계약")
    manager = models.IntegerField(default=0, verbose_name="관리인")
    physical_therapist = models.IntegerField(default=0, verbose_name="물리치료사")
    assistant = models.IntegerField(default=0, verbose_name="보조원")
    general_manager = models.IntegerField(default=0, verbose_name="사무국장")
    office = models.IntegerField(default=0, verbose_name="사무실")
    office_worker = models.IntegerField(default=0, verbose_name="사무원")
    social_worker = models.IntegerField(default=0, verbose_name="사회복지사")
    washing_room = models.IntegerField(default=0, verbose_name="세면/세탁실")
    head_of_facility = models.IntegerField(default=0, verbose_name="시설장")
    nutritionist = models.IntegerField(default=0, verbose_name="영양사")
    sanitation_worker = models.IntegerField(default=0, verbose_name="위생원")
    suspended = models.IntegerField(default=0, verbose_name="유예")
    occupational_therapist = models.IntegerField(default=0, verbose_name="작업치료사")
    day_night_care = models.IntegerField(default=0, verbose_name="재가노인복지시설주야간보호")
    cook = models.IntegerField(default=0, verbose_name="조리원")
    bedroom = models.IntegerField(default=0, verbose_name="침실")
    toilet = models.IntegerField(default=0, verbose_name="화장실")

    def __str__(self):
        return self.facility_name

    class Meta:
        verbose_name = "실버케어 시설"
        verbose_name_plural = "실버케어 시설 목록"