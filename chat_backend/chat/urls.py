from django.urls import path
from .views import RegisterView, LoginView,createUserView,AdminListView,UserListView,DeleteUserView,addAccountView,GetUserView,UpdateUserView, GetMessageView, StartChatAPIView


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('create_account/', createUserView.as_view()),
    path('admin-list/', AdminListView.as_view()),
    path('user-list/', UserListView.as_view()),
    path('delete-user/<int:pk>/', DeleteUserView.as_view()),
    path('add-account/', addAccountView.as_view()),
    path('update-account/<int:pk>/', UpdateUserView.as_view() ),
    path('get-user/<int:pk>/', GetUserView.as_view()),
    path("messages/<int:conversation_id>/", GetMessageView.as_view()),
    path('start-chat/<int:user_id>/', StartChatAPIView.as_view()),
]