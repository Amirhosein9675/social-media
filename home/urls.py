from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('detail/<int:post_id>/<slug:post_slug>/',
         views.DetailPostView.as_view(), name='detail_post'),
    path('delete/<int:post_id>/', views.DeletePostView.as_view(), name='delete_post'),
    path('update/<int:post_id>/', views.UpdatePostView.as_view(), name='update_post'),
    path('create/', views.CreatePostView.as_view(), name='create_post'),
]
