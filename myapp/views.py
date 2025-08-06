import requests
from .forms import ProtectedProfileForm, SelfProfileForm
from .models import ProtectedProfile, SelfProfile
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# 카카오 API 설정
REST_API_KEY = "a9e637eee7e057c532f2fc68ef7441fb"
# LOGIN_REDIRECT_URI = "http://localhost:8000/kakao_login/"
# LOGOUT_REDIRECT_URI = "http://localhost:8000/"
LOGIN_REDIRECT_URI = "https://workexperience.onrender.com/kakao_login/"
LOGOUT_REDIRECT_URI = "https://workexperience.onrender.com/"

def main(request):
    return render(request, 'main.html')

def recent(request):
    recent_homes = []  # 실제 로직으로 변경 필요
    return render(request, 'recent.html', {'recent_homes': recent_homes})

def scrapped(request):
    scrapped_homes = []  # 실제 로직으로 변경 필요
    return render(request, 'scrapped.html', {'scrapped_homes': scrapped_homes})

def reviews(request):
    user_reviews = []  # 실제 로직으로 변경 필요
    return render(request, 'reviews.html', {'user_reviews': user_reviews})

def add_profile(request):
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

    return render(request, 'add_profile.html', {
        'protected_form': protected_form
    })

def kakao_login(request):
    # 카카오 인증 코드가 있는지 확인
    code = request.GET.get('code')
    if code:    
        # 인증 코드로 액세스 토큰 요청
        token_response = requests.post(
        url = "https://kauth.kakao.com/oauth/token", 
        data = {
            'grant_type': 'authorization_code',
            'client_id': REST_API_KEY,
            'redirect_uri': LOGIN_REDIRECT_URI,
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
            id=request.session['kakao_id'],
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
        return redirect(f'https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={LOGIN_REDIRECT_URI}&response_type=code&scope=openid')

def kakao_logout(request):
    logout(request)
    kakao_logout_url = f"https://kauth.kakao.com/oauth/logout?client_id={REST_API_KEY}&logout_redirect_uri={LOGOUT_REDIRECT_URI}"
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
    
def search(request):
    return render(request, 'search.html')

def mypage(request):
    self_profile = SelfProfile.objects.get(user=request.user)
    protected_profiles = ProtectedProfile.objects.filter(user=request.user)

    return render(request, 'mypage.html', {
        'self_profile': self_profile,
        'protected_profiles': protected_profiles
    })

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