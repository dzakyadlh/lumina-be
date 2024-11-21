from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import CustomUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
            return Response({'message':'Signed Up Successfully', 'data':serializer.data if serializer.data is not None else {}}, status=status.HTTP_201_CREATED)
        return Response({'message':'Signed Up Failed', 'data':serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def signin(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'message':'Login success',
            'data':user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    else:
        return Response({'message':'Invalid credentials'}, status=400)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    serializer = CustomUserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({'message':'User Data Updated Successfully', 'data':serializer.data if serializer.data is not None else {}}, status=status.HTTP_200_OK)
    return Response({'message':'User Data Update Failed', 'data':serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def signout(request):
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklists the refresh token
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'message': 'Sign out failed', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)