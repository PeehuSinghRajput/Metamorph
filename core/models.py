"""
Models for the Metamorph project.

This module defines the data models for storing unified data from various public APIs,
user profiles, product details, transactions, and logs/cache for API requests.
"""

from django.db import models
from django.utils.timezone import now
import uuid

class BaseModel(models.Model):
    """
    Abstract base model that adds common timestamp fields to all models.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UnifiedEntity(BaseModel):
    """
    Model to store unified data from different APIs.

    Attributes:
        entity_id: A unique identifier generated for the unified record.
        entity_type: The type of entity ('product', 'user', or 'transaction').
        timestamp: The ISO-8601 timestamp when the record was created.
        data: The normalized data payload from the source.
        metadata: Additional metadata such as the source and processing timestamp.
    """
    ENTITY_TYPES = [
        ('product', 'Product'),
        ('user', 'User'),
        ('transaction', 'Transaction')
    ]
    entity_id = models.CharField(max_length=100, unique=True, db_index=True)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    timestamp = models.DateTimeField(default=now)
    data = models.JSONField()
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.entity_type} - {self.entity_id}"

class UserProfile(BaseModel):
    """
    Model to store user profile data fetched from the external API.
    
    Attributes:
        external_id: The unique identifier provided by the external API.
        name: The user's full name.
        email: The user's email address.
        phone: The user's phone number.
        country: The user's country.
        registered_date: The date when the user registered.
    """
    external_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100)
    registered_date = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

class Category(BaseModel):
    """
    Model to categorize products.
    
    Attributes:
        name: The unique name of the category.
    """
    name = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name

class Product(BaseModel):
    """
    Model to store product data fetched from the external API.
    
    Attributes:
        external_id: The unique identifier provided by the external API.
        title: The product title.
        price: The product price.
        category: ForeignKey to the Category model.
        description: The product description.
        image_url: The URL to the product image.
    """
    external_id = models.IntegerField(unique=True, db_index=True)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    description = models.TextField(blank=True)
    image_url = models.URLField()

    def __str__(self):
        return self.title

class Transaction(BaseModel):
    """
    Model to store transaction data.
    
    Attributes:
        external_id: The unique transaction ID provided by the external API.
        user: ForeignKey to the UserProfile model.
        product: ForeignKey to the Product model.
        amount: The transaction amount.
        timestamp: The timestamp when the transaction occurred.
    """
    external_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='transactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.name} - {self.product.title} - {self.amount}"

class APIRequestLog(BaseModel):
    """
    Model to log API requests for debugging and analytics.
    
    Attributes:
        endpoint: The API endpoint that was accessed.
        request_method: The HTTP method used (GET or POST).
        response_status: The HTTP response status code.
        response_time: The time taken to process the request.
        created_by: ForeignKey to the UserProfile if the request was made by an authenticated user.
    """
    endpoint = models.CharField(max_length=255)
    request_method = models.CharField(max_length=6, choices=[('GET', 'GET'), ('POST', 'POST')])
    response_status = models.IntegerField()
    response_time = models.FloatField(help_text="Response time in seconds")
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.endpoint} - {self.response_status}"

class APIDataCache(BaseModel):
    """
    Model to cache API responses for efficiency.
    
    Attributes:
        endpoint: The API endpoint whose response is cached.
        response_data: The JSON response data.
        fetched_at: The timestamp when the data was fetched.
    """
    endpoint = models.CharField(max_length=255, db_index=True)
    response_data = models.JSONField()
    fetched_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cache for {self.endpoint}"
