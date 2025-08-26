# urls.py do app
from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # rotas de template (para interface web)
    path("", views.create, name="create"),
    path("usuarios/create/", views.create, name="create_usuarios"),
    path("usuarios/<int:id>/alterar-senha/", views.alterar_senha, name="alterar_senha"),
    
    # rotas de autenticação e hierarquia
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("gerenciar-subcontas/", views.gerenciar_subcontas, name="gerenciar_subcontas"),
    path("criar-admin-inicial/", views.criar_admin_inicial, name="criar_admin_inicial"),
    
    # rotas de API (para React)
    path("api/usuarios/", api_views.usuario_list_create, name="api_usuarios"),
    path("api/usuarios/<int:pk>/", api_views.usuario_detail, name="api_usuario_detail"),
    path("api/usuarios/<int:pk>/alterar-senha/", api_views.alterar_senha_api, name="api_alterar_senha"),
    path("api/validar-senha/", api_views.validar_senha_api, name="api_validar_senha"),
    path("api/login/", api_views.login_api, name="api_login"),
    path("api/logout/", api_views.logout_api, name="api_logout"),
    path("api/subcontas/", api_views.subcontas_api, name="api_subcontas"),
    path("api/criar-admin-inicial/", api_views.criar_admin_inicial_api, name="api_criar_admin_inicial"),
]
