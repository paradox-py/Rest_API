import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer,UserLoginSerializer  
from django.contrib.auth.models import auth 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .models import User 
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg , Q
from django.core.serializers import serialize



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {

        'refresh' : str(refresh),
        'access' : str(refresh.access_token),

    }

#User registration view:
class UserRegistrationView(APIView):
    def post(self, request, format=None):
        try:
            email = request.data.get('email')
            if User.objects.filter(email=email).exists():
                return Response({'status': False, 'code': status.HTTP_400_BAD_REQUEST, 'message': 'User with this email already exists','data' : {}})
            serializer = UserRegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token = get_tokens_for_user(user)

            data = {

                'status': True,
                'code': status.HTTP_200_OK, 
                'message': 'User created successfully',
                'data' : serializer.data,
                'jwt' :  token
            }
            return Response(data)
        except Exception as e:
            return Response({'status': False, 'code': status.HTTP_400_BAD_REQUEST, 'message': str(e), 'data': {}})
        


#User login view:
class UserLoginView(APIView):
    def post(self, request, format=None):
        try:
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = auth.authenticate(email=email, password=password)
            
            if user is not None:
                token = get_tokens_for_user(user)

                data = { 'email': user.email,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'jwt': token
                        }
                
                return Response({
                    'status': True,
                    'code': status.HTTP_200_OK,
                    'message': 'User successfully logged in',
                    'data' : data
                   
                })
            else:
                return Response({
                    'status': False,
                    'code': status.HTTP_401_UNAUTHORIZED,
                    'message': 'Authentication failed',
                    'data': {}
                })
        except Exception as e:
            return Response({
                'status': False,
                'code': status.HTTP_400_BAD_REQUEST,
                'message': str(e),
                'data': {}
            })


class UserLogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({'success': False,'code': status.HTTP_400_BAD_REQUEST, 'message': 'Refresh token not provided'})
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({'success': True,'code':status.HTTP_200_OK, 'message': 'User logged out successfully'})
        except Exception as e:
            return Response({'success': False,'code': status.HTTP_400_BAD_REQUEST, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class MeanScoreAPIView(APIView):
    def get(self, request, format=None):
        mean_score_dict = User.objects.aggregate(mean_score=Avg('score'))
        mean_score = mean_score_dict['mean_score'] if 'mean_score' in mean_score_dict else None
        highest_score_user = User.objects.order_by('-score').first()
        has_low_score = User.objects.filter(score__lt=2).exists()
        users_with_same_score = User.objects.filter(score=mean_score) if mean_score is not None else []
        users_without_scores = User.objects.exclude(Q(score=10) | Q(score=20) | Q(score__isnull=True)) 
        users =  User.objects.all()[10:]
        serialized_users = serialize('json', users,fields=('username', 'score'))
        deserialized_users = json.loads(serialized_users)
        user_list = [user_obj['fields'] for user_obj in deserialized_users]

        
        user_list_same_Score = [
            {
                'username': user.email,
                'score': user.score
            }
            for user in users_with_same_score
        ]
        user_list_exclude = [
            {
                'username': user.email,
                'score': user.score
            }
            for user in users_without_scores
        ]

        data = {
            'status': True,
            'code': status.HTTP_200_OK,
            'mean_score': mean_score,
            'highest_score': highest_score_user.email if highest_score_user else None,
            'low_score': has_low_score,
            'users_with_same_score': user_list_same_Score,
            'exculed' : user_list_exclude,
            'excluded_first_ten' : user_list
        }
        return Response(data)
