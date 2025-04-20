from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ChatUser,Conversation, Message
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer, createUserSerializer, MessageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
import json


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                conversation = Conversation.objects.filter(user=user).first()
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": user.username,
                    "role": "admin" if user.is_admin else "user",
                    "conversation_id": conversation.id if conversation else None
                }, status=status.HTTP_200_OK)
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class createUserView(APIView):
    def post(self, request):
        serializer = createUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User created successfully!',
                'username': user.username,
                'is_admin': user.is_admin
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AdminListView(APIView):
    def get(self, request):
        admins = ChatUser.objects.filter(is_admin=True)
        serializer = createUserSerializer(admins, many=True)
        return Response(serializer.data)
    
class UserListView(APIView):
    def get(self, request):
        users = ChatUser.objects.filter(is_admin=False)
        serializer = createUserSerializer(users, many=True)
        return Response(serializer.data)
    
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        if not request.user.is_admin:
            return Response({'error': 'Chỉ admin mới được xóa người dùng!'}, status=status.HTTP_403_FORBIDDEN)

        if int(request.user.id) == int(pk):
            return Response({'error': 'Bạn không thể xóa chính mình!'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = ChatUser.objects.get(pk=pk)
            user.delete()
            return Response({'message': 'Xóa thành công!'}, status=status.HTTP_200_OK)
        except ChatUser.DoesNotExist:
            return Response({'error': 'Người dùng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)



class addAccountView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
   
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        if not username or not email or not password:
            return Response({"error": "Thiếu thông tin"}, status=400)
           
        if ChatUser.objects.filter(username=username).exists():
            return Response({"error": "Tên người dùng đã tồn tại"}, status=400)
           
        user = ChatUser(
            username=username,
            email=email 
        )

        if role == '1':
            user.is_admin = True
        else:
            user.is_admin = False

        user.set_password(password)
        user.save()              
        return Response({"message": "Tạo tài khoản thành công"}, status=201)

class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        # Kiểm tra quyền của người dùng
        if not request.user.is_admin and int(request.user.id) != int(pk):
            return Response({'error': 'Chỉ admin hoặc chính người dùng đó mới có quyền sửa!'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = ChatUser.objects.get(pk=pk)
        except ChatUser.DoesNotExist:
            return Response({'error': 'Người dùng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        username = data.get('username')
        email = data.get('email')
        role = data.get('role')  # Chỉ admin mới có thể cập nhật quyền

        # Nếu là admin, có thể sửa thông tin admin và role
        if request.user.is_admin:
            if role is not None:
                user.is_admin = True if role == '1' else False
        
        # Kiểm tra username trùng với người khác
        if ChatUser.objects.filter(username=username).exclude(id=pk).exists():
            return Response({'error': 'Tên người dùng đã tồn tại!'}, status=status.HTTP_400_BAD_REQUEST)

        if username:
            user.username = username
        if email:
            user.email = email

        user.save()

        return Response({
            'message': 'Cập nhật thành công!',
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }, status=status.HTTP_200_OK)

class GetUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            user = ChatUser.objects.get(pk=pk)
        except ChatUser.DoesNotExist:
            return Response({'error': 'Người dùng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_admin and int(request.user.id) != int(pk):
            return Response({'error': 'Chỉ admin hoặc chính người dùng đó mới có quyền xem thông tin!'}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }, status=status.HTTP_200_OK)

class GetMessageView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, conversation_id):
        messages = Message.objects.filter(conversation_id=conversation_id).order_by("created_at")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
class StartChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            user = ChatUser.objects.get(id=user_id)

            # Tạo hoặc lấy cuộc hội thoại giữa admin hiện tại và user
            conversation, created = Conversation.objects.get_or_create(
                user=user,
                admin=request.user
            )

            return Response({
                'success': True,
                'conversation_id': conversation.id,
                'username': user.username
            }, status=status.HTTP_200_OK)

        except ChatUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User không tồn tại'
            }, status=status.HTTP_404_NOT_FOUND)

