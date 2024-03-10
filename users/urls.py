from django.urls import path

from users.apps import UsersConfig

from users.views import UserCreateAPIView, UserListAPIView,\
    UserRetrieveAPIView, UserUpdateAPIView,\
    UserDestroyAPIView, UserGetID

app_name = UsersConfig.name


urlpatterns = [
    path('create/', UserCreateAPIView.as_view(), name='user_create'),
    path('list/', UserListAPIView.as_view(), name='user_list'),
    path('<int:pk>/', UserRetrieveAPIView.as_view(), name='user_get'),
    path('update/<int:pk>/', UserUpdateAPIView.as_view(), name='user_update'),
    path('delete/<int:pk>/', UserDestroyAPIView.as_view(), name='user_delete'),
    path('get_id/', UserGetID.as_view(), name='user_get_id'),
              ]
