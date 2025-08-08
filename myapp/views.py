import os
import requests
import pandas as pd
import json
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

def main(request):
    """
    CSV 파일을 읽어와 시설명을 검색하고 결과를 템플릿에 전달하는 뷰.
    """
    # GET 요청에서 'q'라는 이름의 쿼리 파라미터(검색어)를 가져옵니다.
    search_query = request.GET.get('q', '').strip()
    context = {
        'search_query': search_query,
        'results': [],
        'results_count': 0
    }

    # CSV 파일의 절대 경로를 구성합니다.
    csv_file_path = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'csv', 'output_combined_final.csv')

    # 검색 쿼리가 있을 경우에만 검색을 수행합니다.
    if search_query:
        try:
            # pandas 라이브러리를 사용하여 CSV 파일을 DataFrame으로 읽습니다.
            df = pd.read_csv(csv_file_path, encoding='utf-8')

            # '시설명' 컬럼에서 검색어를 포함하는 행을 찾습니다.
            search_results = df[df['시설명'].str.contains(search_query, na=False, case=False)]

            # 결과를 딕셔너리 리스트로 변환
            results = search_results.to_dict('records')
            
            # NaN 값을 None으로 변환 (JSON 직렬화를 위해)
            for result in results:
                for key, value in result.items():
                    if pd.isna(value):
                        result[key] = None
            
            context['results'] = results
            context['results_count'] = len(results)

        except FileNotFoundError:
            context['error'] = f"CSV 파일을 찾을 수 없습니다: {csv_file_path}"
        except Exception as e:
            context['error'] = f"파일 처리 중 오류가 발생했습니다: {str(e)}"

    return render(request, 'main.html', context)

def search_facilities_ajax(request):
    """
    AJAX 요청을 위한 검색 API
    """
    if request.method == 'GET':
        search_query = request.GET.get('q', '').strip()
        
        if not search_query:
            return JsonResponse({
                'results': [],
                'results_count': 0,
                'search_query': search_query
            })

        csv_file_path = os.path.join(settings.BASE_DIR, 'myapp', 'static', 'csv', 'output_combined_final.csv')

        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8')
            search_results = df[df['시설명'].str.contains(search_query, na=False, case=False)]
            results = search_results.to_dict('records')
            
            # NaN 값을 None으로 변환
            for result in results:
                for key, value in result.items():
                    if pd.isna(value):
                        result[key] = None
            
            return JsonResponse({
                'results': results,
                'results_count': len(results),
                'search_query': search_query
            })

        except Exception as e:
            return JsonResponse({
                'error': f"검색 중 오류가 발생했습니다: {str(e)}",
                'results': [],
                'results_count': 0,
                'search_query': search_query
            }, status=500)

    return JsonResponse({'error': 'GET 요청만 지원됩니다.'}, status=405)

@login_required
def mypage(request):
    self_profile = SelfProfile.objects.get(user=request.user)
    protected_profiles = ProtectedProfile.objects.filter(user=request.user)

    return render(request, 'mypage.html', {
        'self_profile': self_profile,
        'protected_profiles': protected_profiles
    })

@login_required
def recent(request):
    recent_homes = []  # 실제 로직으로 변경 필요
    return render(request, 'recent.html', {'recent_homes': recent_homes})

@login_required
def scrapped(request):
    scrapped_homes = []  # 실제 로직으로 변경 필요
    return render(request, 'scrapped.html', {'scrapped_homes': scrapped_homes})

@login_required
def reviews(request):
    user_reviews = []  # 실제 로직으로 변경 필요
    return render(request, 'reviews.html', {'user_reviews': user_reviews})

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