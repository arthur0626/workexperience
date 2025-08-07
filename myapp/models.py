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
