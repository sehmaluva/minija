from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from apps.users.models.models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer, 
    UserUpdateSerializer,
    ChangePasswordSerializer
)

class RegisterView(generics.CreateAPIView):
    """
    API view for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    API view for user login
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    API view for user logout
    """
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except:
        return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """
    API view for changing password
    """
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Update token
        try:
            user.auth_token.delete()
        except:
            pass
        
        token = Token.objects.create(user=user)
        
        return Response({
            'message': 'Password changed successfully',
            'token': token.key
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    """
    API view for listing users (admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return User.objects.all()
        return User.objects.filter(id=user.id)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions_view(request):
    """
    API view to get user permissions based on role
    """
    user = request.user
    permissions_map = {
        'admin': {
            'can_manage_users': True,
            'can_manage_farms': True,
            'can_manage_flocks': True,
            'can_view_reports': True,
            'can_manage_health': True,
            'can_manage_production': True,
        },
        'manager': {
            'can_manage_users': False,
            'can_manage_farms': True,
            'can_manage_flocks': True,
            'can_view_reports': True,
            'can_manage_health': True,
            'can_manage_production': True,
        },
        'veterinarian': {
            'can_manage_users': False,
            'can_manage_farms': False,
            'can_manage_flocks': False,
            'can_view_reports': True,
            'can_manage_health': True,
            'can_manage_production': False,
        },
        'worker': {
            'can_manage_users': False,
            'can_manage_farms': False,
            'can_manage_flocks': False,
            'can_view_reports': False,
            'can_manage_health': False,
            'can_manage_production': True,
        },
        'owner': {
            'can_manage_users': True,
            'can_manage_farms': True,
            'can_manage_flocks': True,
            'can_view_reports': True,
            'can_manage_health': True,
            'can_manage_production': True,
        },
    }
    
    user_permissions = permissions_map.get(user.role, {})
    
    return Response({
        'user': UserSerializer(user).data,
        'permissions': user_permissions
    }, status=status.HTTP_200_OK)
