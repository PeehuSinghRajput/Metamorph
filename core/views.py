"""
API Views for the Metamorph Project

This module implements class-based views to handle:
- API overview for endpoint discovery.
- Unified data retrieval by entity type.
- User spending insights.
- Product popularity metrics.
- Transaction data enrichment.

All views (excluding the overview) require JWT authentication for access control.
"""

import logging
from django.db.models import Sum, Avg, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.models import UnifiedEntity, Transaction, UserProfile, Category
from core.serializers import UnifiedEntitySerializer
from core.services import enrich_transactions

logger = logging.getLogger(__name__)

class OverviewView(APIView):
    """
    API Overview

    Provides an overview of the available API endpoints.

    Endpoint: `/api/`
    Method: GET

    Returns:
        - A dictionary containing a welcome message and available endpoints.
    """
    def get(self, request):
        return Response({
            "message": "Welcome to Metamorph API",
            "endpoints": {
                "/api/data/{entity_type}/": "Retrieve processed data by type",
                "/api/insights/users/": "Retrieve user spending insights",
                "/api/insights/products/": "Retrieve product popularity metrics",
                "/api/enrich/transactions/": "Trigger transaction data enrichment",
                "/api/token/": "Obtain JWT token",
                "/api/token/refresh/": "Refresh JWT token"
            }
        }, status=status.HTTP_200_OK)

class DataByTypeView(APIView):
    """
    Unified Data Retrieval by Entity Type

    Endpoint: `/api/data/<entity_type>/`
    Method: GET

    Description:
        Retrieves data filtered by a specific entity type. 
        Allowed entity types: 'product', 'user', 'transaction'.

    Authentication:
        - Requires JWT Authentication
        - Requires IsAuthenticated permission

    Returns:
        - JSON serialized data for the requested entity type.
        - HTTP 400 if entity type is invalid.
        - HTTP 500 in case of server-side errors.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type):
        if entity_type not in ['product', 'user', 'transaction']:
            return Response(
                {"error": "Invalid entity_type. Allowed types: 'product', 'user', 'transaction'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            data_qs = UnifiedEntity.objects.filter(entity_type=entity_type)
            serializer = UnifiedEntitySerializer(data_qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Error retrieving data for entity_type: %s", entity_type)
            return Response(
                {"error": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserInsightsView(APIView):
    """
    User Spending Insights

    Endpoint: `/api/insights/users/`
    Method: GET

    Description:
        Aggregates and retrieves user spending insights.

    Authentication:
        - Requires JWT Authentication
        - Requires IsAuthenticated permission

    Returns:
        - List of users with aggregated total spending.
        - HTTP 500 in case of server-side errors.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_data = UserProfile.objects.all().annotate(
                total_spent=Sum('transactions__amount')
            ).values('external_id', 'name', 'email', 'total_spent')
            return Response(list(user_data), status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Error computing user insights")
            return Response(
                {"error": "An error occurred while computing user insights."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProductInsightsView(APIView):
    """
    Product Popularity Insights

    Endpoint: `/api/insights/products/`
    Method: GET

    Description:
        Provides metrics on product popularity and average transaction value.

    Authentication:
        - Requires JWT Authentication
        - Requires IsAuthenticated permission

    Returns:
        - List of product categories with their transaction counts.
        - Average transaction value.
        - HTTP 500 in case of server-side errors.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            category_data = Category.objects.annotate(
                transaction_count=Count('products__transactions')
            ).values('name', 'transaction_count')
            avg_transaction = Transaction.objects.aggregate(
                average_value=Avg('amount')
            )
            insights = {
                "product_categories": list(category_data),
                "average_transaction_value": avg_transaction.get("average_value") or 0
            }
            return Response(insights, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Error computing product insights")
            return Response(
                {"error": "An error occurred while computing product insights."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EnrichTransactionsView(APIView):
    """
    Transaction Data Enrichment

    Endpoint: `/api/enrich/transactions/`
    Method: POST

    Description:
        Triggers the enrichment of transaction data by joining transactions 
        with corresponding user and product details.

    Authentication:
        - Requires JWT Authentication
        - Requires IsAuthenticated permission

    Returns:
        - Success message with the count of enriched transactions.
        - HTTP 500 in case of server-side errors.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            count = enrich_transactions()
            return Response(
                {"message": f"Successfully enriched {count} transaction records."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception("Error enriching transactions")
            return Response(
                {"error": "An error occurred during the transaction enrichment process."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
