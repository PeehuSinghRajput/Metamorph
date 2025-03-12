"""
Business Logic & Data Enrichment Services for the Metamorph project.

This module provides functions to:
    - Transform raw API data into a unified format.
    - Store the transformed data in the UnifiedEntity model.
    - Enrich transaction records by joining them with related user and product details.
    - Compute business metrics as needed.
"""

import uuid
from django.utils.timezone import now
from core.models import UnifiedEntity, Transaction, UserProfile, Product
import logging

logger = logging.getLogger(__name__)

def transform_data(api_name, raw_data):
    """
    Transforms raw API data into the unified format.

    Args:
        api_name (str): The API source name ('products', 'users', or 'transactions').
        raw_data (list or dict): The raw data fetched from the API.

    Returns:
        list: A list of dictionaries, each conforming to the unified format.
    """
    transformed_data = []

    if api_name == "products":
        for item in raw_data:
            transformed_data.append({
                "entity_id": str(uuid.uuid4()),
                "entity_type": "product",
                "timestamp": now().isoformat(),
                "data": {
                    "external_id": item["id"],
                    "title": item["title"],
                    "price": item["price"],
                    "category": item["category"],
                    "description": item["description"],
                    "image_url": item["image"]
                },
                "metadata": {
                    "source": "FakeStoreAPI",
                    "processed_at": now().isoformat()
                }
            })
    elif api_name == "users":
        for item in raw_data.get("results", []):
            transformed_data.append({
                "entity_id": str(uuid.uuid4()),
                "entity_type": "user",
                "timestamp": now().isoformat(),
                "data": {
                    "external_id": item["login"]["uuid"],
                    "name": f"{item['name']['first']} {item['name']['last']}",
                    "email": item["email"],
                    "phone": item.get("phone"),
                    "country": item["location"]["country"],
                    "registered_date": item["registered"]["date"]
                },
                "metadata": {
                    "source": "RandomUserAPI",
                    "processed_at": now().isoformat()
                }
            })
    elif api_name == "transactions":
        for item in raw_data:
            simulated_amount = float(item.get("id", 1)) * 10.0
            transformed_data.append({
                "entity_id": str(uuid.uuid4()),
                "entity_type": "transaction",
                "timestamp": now().isoformat(),
                "data": {
                    "external_id": item["id"],
                    "status": item["status"],
                    "eta": item["eta"],
                    "user_name": item["user_name"],
                    "user_phone": item["user_phone"],
                    "amount": simulated_amount,
                    "parcel_id": item.get("parcel_id")
                },
                "metadata": {
                    "source": "MockarooAPI",
                    "processed_at": now().isoformat()
                }
            })
    return transformed_data

def store_transformed_data(transformed_data):
    """
    Stores the transformed data into the UnifiedEntity model, ensuring no duplicates.

    Args:
        transformed_data (list): A list of dictionaries in the unified format.
    """
    for item in transformed_data:
        ext_id = item["data"].get("external_id")
        if ext_id and not UnifiedEntity.objects.filter(data__external_id=ext_id).exists():
            UnifiedEntity.objects.create(**item)

def enrich_transactions():
    """
    Enriches transaction data by joining each Transaction record with its associated 
    user and product details, and stores the result in the UnifiedEntity model.

    Process:
      1. Delete any existing UnifiedEntity records with entity_type 'transaction'.
      2. Query all Transaction records with related UserProfile and Product data.
      3. For each Transaction, build an enriched data dictionary containing:
           - Transaction details (amount, timestamp)
           - Embedded user details (external_id, name, email, phone, country, registered_date)
           - Embedded product details (external_id, title, price, description, category, image_url)
      4. Create a new UnifiedEntity record for the enriched data.

    Returns:
        int: The total number of transaction records enriched.
    """
    UnifiedEntity.objects.filter(entity_type="transaction").delete()
    
    enriched_count = 0
    transactions = Transaction.objects.select_related('user', 'product', 'product__category').all()
    
    for trans in transactions:
        enriched_data = {
            "transaction_id": str(trans.external_id),
            "amount": str(trans.amount),
            "timestamp": trans.timestamp.isoformat(),
            "user": {
                "external_id": str(trans.user.external_id),
                "name": trans.user.name,
                "email": trans.user.email,
                "phone": trans.user.phone,
                "country": trans.user.country,
                "registered_date": trans.user.registered_date.isoformat(),
            },
            "product": {
                "external_id": trans.product.external_id,
                "title": trans.product.title,
                "price": str(trans.product.price),
                "description": trans.product.description,
                "category": trans.product.category.name if trans.product.category else None,
                "image_url": trans.product.image_url,
            }
        }
        UnifiedEntity.objects.create(
            entity_id=str(uuid.uuid4()),
            entity_type="transaction",
            timestamp=trans.timestamp,
            data=enriched_data,
            metadata={
                "source": "Enriched Data",
                "processed_at": now().isoformat()
            }
        )
        enriched_count += 1
        
    return enriched_count
