from django.urls import path

from . import views

urlpatterns = [
    path("", views.render_chart, name='render_chart'),
    path("index/", views.render_index, name='render_index'),
    path("token_metrics/", views.summarize_token_metrics, name='token_metrics'),
    path("token_chart/", views.render_metrics, name='token_chart'),
]
