from django.urls import path, re_path, include
from lists import views as list_views  #(1)
from lists import urls as list_urls  #(1)

urlpatterns = [
    path('', list_views.home_page, name='home'),
    path('lists/', include(list_urls)),  #(2)
]