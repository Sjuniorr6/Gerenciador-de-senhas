from django.urls import path
from . import api_views

app_name = 'steam'

urlpatterns = [
    # APIs principais
    path('api/streaming/', api_views.streaming_list_create, name='streaming_list_create'),
    path('api/streaming/<int:pk>/', api_views.streaming_detail, name='streaming_detail'),
    
    # APIs de compartilhamento
    path('api/streaming/<int:pk>/compartilhar/', api_views.streaming_compartilhar, name='streaming_compartilhar'),
    path('api/streaming/<int:pk>/descompartilhar/<int:usuario_id>/', api_views.streaming_descompartilhar, name='streaming_descompartilhar'),
    
    # APIs auxiliares
    path('api/streaming/plataformas/', api_views.streaming_plataformas, name='streaming_plataformas'),
    path('api/streaming/status/', api_views.streaming_status, name='streaming_status'),
]
