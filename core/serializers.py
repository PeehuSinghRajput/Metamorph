"""
Serializers for the Metamorph project.

This module defines serializers for converting model instances (e.g., UnifiedEntity,
UserProfile, Product, Transaction, Category) into JSON format suitable for API responses.
"""

from rest_framework import serializers
from core.models import UnifiedEntity, UserProfile, Product, Transaction, Category

class UnifiedEntitySerializer(serializers.ModelSerializer):
    """
    Serializer for the UnifiedEntity model.
    
    Converts a UnifiedEntity instance into its JSON representation with fields:
    entity_id, entity_type, timestamp, data, and metadata.
    """
    class Meta:
        model = UnifiedEntity
        fields = ['entity_id', 'entity_type', 'timestamp', 'data', 'metadata']

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.
    """
    class Meta:
        model = UserProfile
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model, including nested category details.
    """
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transaction model, including nested user and product details.
    """
    user = UserProfileSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
