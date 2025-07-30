from django.shortcuts import render, redirect
from .forms import UserSurveyForm
from .models import UserSurvey
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import requests
from django.contrib.auth import login
from django.contrib.auth.models import User

# Create your views here.
def main(request):
    return render(request, 'main.html')

def kakao_login(request):
    # 카카오 로그인 URL로 리다이렉트
    return redirect('https://kauth.kakao.com/oauth/authorize?client_id=a9e637eee7e057c532f2fc68ef7441fb&redirect_uri=https://workexperience.onrender.com/survey/&response_type=code')

def kakao_logout(request):
    logout(request)
    kakao_logout_url = "https://kauth.kakao.com/oauth/logout?client_id=a9e637eee7e057c532f2fc68ef7441fb&logout_redirect_uri=https://workexperience.onrender.com/"
    return redirect('main')

def search(request):
    return render(request, 'search.html')

def mypage(request):
    user = request.user  # 현재 로그인한 사용자
    survey = None
    if user.is_authenticated:
        try:
            survey = UserSurvey.objects.get(user=user)
        except UserSurvey.DoesNotExist:
            survey = None
    return render(request, 'mypage.html', {'survey': survey})

def survey(request):
    if not request.user.is_authenticated:
        code = request.GET.get('code')
        if not code:
            return redirect('main')

        token_url = 'https://kauth.kakao.com/oauth/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': 'a9e637eee7e057c532f2fc68ef7441fb',
            'redirect_uri': 'https://workexperience.onrender.com/survey/',  # 실제 등록된 리디렉션 URI
            'code': code,
        }
        token_response = requests.post(token_url, data=data)
        token_json = token_response.json()

        access_token = token_json.get('access_token')
        if not access_token:
            return render(request, 'main.html', {'message': '토큰 발급 실패'})

        user_info_response = requests.get(
            'https://kapi.kakao.com/v2/user/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_info = user_info_response.json()

        kakao_id = user_info.get('id')
        kakao_account = user_info.get('kakao_account', {})
        profile_info = kakao_account.get('profile', {})

        nickname = profile_info.get('nickname', f'kakao_{kakao_id}')
        profile_image = profile_info.get('profile_image_url', '')

        username = f'kakao_{kakao_id}'

        user, created = User.objects.get_or_create(username=username)
        user.first_name = nickname  # 닉네임 저장
        user.profile_image = profile_image  # 프로필 이미지 저장
        user.save()

        # 로그인 처리
        login(request, user)

        # 사용자 프로필 생성 또는 업데이트
        user_survey, _ = UserSurvey.objects.get_or_create(user=user)
        if profile_image:
            user_survey.profile_image_url = profile_image
            user_survey.save()

    try:
        profile = UserSurvey.objects.get(user=request.user)
        return redirect('main')
    except UserSurvey.DoesNotExist:
        pass

    if request.method == 'POST':
        form = UserSurveyForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('main')
    else:
        form = UserSurveyForm()

    return render(request, 'survey.html', {'form': form})