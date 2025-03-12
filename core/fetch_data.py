"""
Module for fetching data from public APIs.

This module provides a function to fetch data from different public APIs,
handle exceptions, and store the responses in the APIDataCache model.
"""

import requests
import logging
from django.utils.timezone import now
from core.models import APIDataCache

logger = logging.getLogger(__name__)

API_ENDPOINTS = {
    "products": "https://fakestoreapi.com/products",
    "users": "https://randomuser.me/api/?results=20",
    "transactions": "https://my.api.mockaroo.com/orders.json?key=e49e6840"
}

def fetch_data_from_api(api_name):
    """
    Fetches data from the specified API and caches the response.

    Args:
        api_name (str): The key identifying the API to fetch ('products', 'users', or 'transactions').

    Returns:
        list or dict: The API response data if successful; an empty list otherwise.
    """
    url = API_ENDPOINTS.get(api_name)
    if not url:
        logger.error("Invalid API name provided: %s", api_name)
        return []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Cache the API response.
        APIDataCache.objects.update_or_create(
            endpoint=url,
            defaults={"response_data": data, "fetched_at": now()}
        )

        logger.info("Successfully fetched data from %s", api_name)
        return data if data else []
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching data from %s: %s", api_name, e)
        return []
