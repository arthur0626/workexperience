import os, json, replicate, requests
from shlex import quote
from elasticsearch import NotFoundError
import pandas as pd
from elasticsearch_dsl import Q
from .documents import SilverCareFacilityDocument
from .forms import ProtectedProfileForm, SelfProfileForm
from .models import ProtectedProfile, SelfProfile
from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def kakao_login(request):
    # 카카오 인증 코드가 있는지 확인
    code = request.GET.get('code')
    if code:    
        # 인증 코드로 액세스 토큰 요청
        token_response = requests.post(
        url = "https://kauth.kakao.com/oauth/token", 
        data = {
            'grant_type': 'authorization_code',
            'client_id': settings.REST_API_KEY,
            'redirect_uri': settings.LOGIN_REDIRECT_URI,
            'code': request.GET.get('code'),
        })

        # 토큰을 세션에 저장
        request.session['access_token'] = token_response.json().get('access_token')

        # 사용자 프로필 정보 요청
        profile_response = requests.get(
        url = 'https://kapi.kakao.com/v2/user/me',
        headers = {
            'Authorization': f'Bearer {request.session["access_token"]}',
            'content-type': 'application/x-www-form-urlencoded;charset=utf-8'
        })

        # 프로필 정보 세션에 저장
        profile_data = profile_response.json().get('kakao_account', {}).get('profile', {})
        request.session['kakao_id'] = profile_response.json().get('id')
        request.session['nickname'] = profile_data.get('nickname', 'Unknown')

        # 사용자 정보로 User 모델에 저장 (없으면 생성)
        user, created = User.objects.get_or_create(
            username=str(request.session['kakao_id'])
        )
        if not SelfProfile.objects.filter(user=user).exists():
            SelfProfile.objects.create(
                user=user,
                kakao_id=request.session['kakao_id'],
                name=request.session['nickname'],
            )
            next_page = 'survey'
        else:
            next_page = 'main'

        # 로그인 처리
        login(request, user)
        return redirect(next_page)
    else:
        # 인증 코드가 없으면 카카오 로그인 페이지로 리다이렉트
        return redirect(f'https://kauth.kakao.com/oauth/authorize?client_id={settings.REST_API_KEY}&redirect_uri={settings.LOGIN_REDIRECT_URI}&response_type=code&scope=openid')

def kakao_logout(request):
    logout(request)
    kakao_logout_url = f"https://kauth.kakao.com/oauth/logout?client_id={settings.REST_API_KEY}&logout_redirect_uri={settings.LOGOUT_REDIRECT_URI}"
    return redirect('main')

def kakao_unlink(request):
    # 카카오 계정 연동 해제
    requests.post(
    url = "https://kapi.kakao.com/v1/user/unlink",
    headers = {
        "Authorization": f"Bearer {request.session['access_token']}"
    })

    # 사용자 정보 삭제
    SelfProfile.objects.get(user=request.user).delete()
    ProtectedProfile.objects.filter(user=request.user).delete()
    
    # 세션 초기화
    request.session.flush()

    return redirect('main')

@login_required
def mypage(request):
    self_profile = SelfProfile.objects.get(user=request.user)
    protected_profiles = ProtectedProfile.objects.filter(user=request.user)

    return render(request, 'mypage.html', {
        'self_profile': self_profile,
        'protected_profiles': protected_profiles
    })

@login_required
def add_profile(request):
    if request.method == 'POST':
        protected_form = ProtectedProfileForm(request.POST)

        if protected_form.is_valid():
            # 피보호자 저장
            protected_profile = protected_form.save(commit=False)
            protected_profile.user = request.user
            protected_profile.save()

            return redirect('mypage')
    else:
        protected_form = ProtectedProfileForm()

    return render(request, 'add_profile.html', {
        'protected_form': protected_form
    })

@login_required
def edit_profile(request, profile_id):
    profile = ProtectedProfile.objects.get(id=profile_id, user=request.user)

    if request.method == 'POST':
        form = ProtectedProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('mypage')
    else:
        form = ProtectedProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {
        'form': form,
        'profile': profile
    })

@login_required
def delete_profile(request, profile_id):
    profile = ProtectedProfile.objects.get(id=profile_id, user=request.user)
    if request.method == 'POST':
        profile.delete()
        return redirect('mypage')
    
    return render(request, 'delete_profile.html', {
        'profile': profile
    })

@login_required
def survey(request):
    if request.method == 'POST':
        protected_form = ProtectedProfileForm(request.POST)

        if protected_form.is_valid():
            # 피보호자 저장
            protected_profile = protected_form.save(commit=False)
            protected_profile.user = request.user
            protected_profile.save()

            return redirect('main')
    else:
        protected_form = ProtectedProfileForm()

    return render(request, 'survey.html', {
        'protected_form': protected_form
    })


def clickpage(request, facility_id):
    try:
        facility_doc = SilverCareFacilityDocument.get(id=facility_id)
        facility_data = facility_doc.to_dict()

        # --- 지도 URL 생성 로직 추가 ---
        address = facility_data.get('address')
        if address:
            # 주소를 URL 인코딩하여 Google Maps Embed URL 생성
            encoded_address = quote(address)
            map_url = f"https://www.google.com/maps?q={encoded_address}&output=embed"
        else:
            map_url = "" # 주소 정보가 없을 경우 빈 URL 전달

        context = {
            'facility': facility_data,
            'map_url': map_url, # 생성된 지도 URL을 context에 추가
        }
        return render(request, 'clickpage.html', context)
        
    except NotFoundError:
        raise Http404("해당 시설을 찾을 수 없습니다.")

def main(request):
    # URL의 GET 파라미터에서 검색어('q')를 가져옵니다.
    search_query = request.GET.get('q', '')
    
    results_list = []

    if search_query:
        # Elasticsearch 'multi_match' 쿼리를 사용하여 facility_name과 address 필드에서 검색
        q = Q('multi_match', 
            query=search_query, 
            fields=['facility_name' ], 
            analyzer='nori'
        )
        search = SilverCareFacilityDocument.search().query(q)
        
        response = search.execute()
        results_list = [hit.to_dict() for hit in response.hits]
    
    # 검색어와 결과 리스트를 템플릿에 전달합니다.
    context = {
        'search_query': search_query,
        'results': results_list,
    }
    
    if request.user.is_authenticated:
        context['protected_profiles'] = ProtectedProfile.objects.filter(user=request.user)
    else:
        context['protected_profiles'] = []

    return render(request, 'main.html', context)


def ai_search(request, profile_id):
    try:
        profile = ProtectedProfile.objects.get(id=profile_id, user=request.user)
    except ProtectedProfile.DoesNotExist:
        raise Http404("프로필을 찾을 수 없습니다.")

    # 1. Elasticsearch에서 모든 시설 데이터 가져오기 (최대 100개로 제한)
    search = SilverCareFacilityDocument.search()[:100]
    response = search.execute()
    facilities = [hit.to_dict() for hit in response.hits]

    # 2. AI에게 전달할 프롬프트 생성
    prompt = f"""
    당신은 대한민국 최고의 노인 요양 시설 추천 전문가입니다. 아래의 '보호 대상자 프로필'과 '시설 목록'을 분석하여, 프로필에 가장 적합한 시설 3곳을 추천해주세요.

    [보호 대상자 프로필]
    - 이름: {profile.name}
    - 나이: {profile.age}
    - 성별: {profile.get_sex_display}
    - 선호 지역: {profile.address} {profile.address_detail}
    - 예산 범위(월): {profile.budget_min}만원 ~ {profile.budget_max}만원
    - 건강 상태: {profile.health_conditions}
    - 희망 서비스: {profile.preferred_services}
    - 기타 사항: {profile.additional_info}

    [시설 목록]
    {json.dumps(facilities, ensure_ascii=False, indent=2)}

    [요청 사항]
    1. '시설 목록'에서 '보호 대상자 프로필'에 가장 적합한 시설 3곳을 선정해주세요.
    2. 각 시설에 대해 다음 기준을 종합적으로 고려하여 평가해주세요:
       - **적합성**: 건강 상태 및 희망 서비스 충족 여부 (예: 거동이 불편하면 물리치료사, 재활 프로그램이 중요)
       - **근접성**: 선호 지역과의 거리
       - **평판 및 환경**: 인터넷 검색을 통해 알 수 있는 평판이나 주변 시설(큰 병원, 교회, 공원 등)을 고려해주세요.
       - **예산**: 예산 범위 내에 있는지 (정확한 비용 정보가 없으면 추정)
    3. 결과를 반드시 아래와 같은 JSON 형식으로만 응답해주세요. 다른 설명은 추가하지 마세요.

    [
        {{
            "facility_name": "추천 시설 이름 1",
            "reason": "이 시설을 추천하는 이유를 2~3문장으로 구체적으로 설명해주세요."
        }},
        {{
            "facility_name": "추천 시설 이름 2",
            "reason": "두 번째 시설을 추천하는 이유를 설명해주세요."
        }},
        {{
            "facility_name": "추천 시설 이름 3",
            "reason": "세 번째 시설을 추천하는 이유를 설명해주세요."
        }}
    ]
    """

    # 3. Replicate API 호출
    try:
        os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN
        output = replicate.run(
            "meta/meta-llama-3-8b-instruct",
            input={"prompt": prompt, "temperature": 0.5, "max_new_tokens": 1024}
        )
        ai_response_str = "".join(output)

        # 4. AI 응답 파싱
        # AI 응답에서 JSON 부분만 정확히 추출
        json_start = ai_response_str.find('[')
        json_end = ai_response_str.rfind(']') + 1
        recommendations_json = ai_response_str[json_start:json_end]

        recommendations = json.loads(recommendations_json)

        # 추천된 시설 이름 목록 추출
        recommended_names = [rec['facility_name'] for rec in recommendations]

        # 전체 시설 목록에서 추천된 시설 정보만 필터링
        recommended_facilities = []
        for rec in recommendations:
            for facility in facilities:
                if facility.get('facility_name') == rec['facility_name']:
                    # AI의 추천 이유를 시설 정보에 추가
                    facility['ai_reason'] = rec['reason']
                    recommended_facilities.append(facility)
                    break

    except Exception as e:
        # AI 호출 실패 시 에러 처리
        print(f"AI API Error: {e}")
        recommendations = []
        recommended_facilities = []

    context = {
        'profile': profile,
        'recommended_facilities': recommended_facilities,
    }

    return render(request, 'ai_search.html', context)