"""
URL configuration for the core app.

This module defines routes for data retrieval, business insights, and data enrichment endpoints.
It also includes JWT token endpoints for authentication.
"""

from django.urls import path
from core.views import (
    OverviewView,
    DataByTypeView,
    UserInsightsView,
    ProductInsightsView,
    EnrichTransactionsView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', OverviewView.as_view(), name='api-overview'),
    path('data/<str:entity_type>/', DataByTypeView.as_view(), name='data-by-type'),
    path('insights/users/', UserInsightsView.as_view(), name='user-insights'),
    path('insights/products/', ProductInsightsView.as_view(), name='product-insights'),
    path('enrich/transactions/', EnrichTransactionsView.as_view(), name='enrich-transactions'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
