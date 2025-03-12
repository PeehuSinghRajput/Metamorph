"""
Celery tasks for the Metamorph project.

This module defines tasks for fetching and processing data from external APIs.
Tasks include fetching data for products, users, and transactions, transforming the data,
and storing it in the UnifiedEntity model.
"""

import logging
from celery import shared_task
from core.fetch_data import fetch_data_from_api
from core.services import transform_data, store_transformed_data

logger = logging.getLogger(__name__)

@shared_task
def fetch_and_store_data(api_name):
    """
    Celery task to fetch data from a specified API, transform it into the unified format,
    and store it in the UnifiedEntity model.

    Args:
        api_name (str): The API source name ('products', 'users', or 'transactions').

    Returns:
        str: A message indicating the result of the task.
    """
    logger.info("Starting fetch_and_store_data task for API: %s", api_name)
    raw_data = fetch_data_from_api(api_name)
    if not raw_data:
        logger.error("No data fetched from %s", api_name)
        return f"Failed to fetch data from {api_name}"
    
    transformed = transform_data(api_name, raw_data)
    store_transformed_data(transformed)
    logger.info("Completed processing for %s", api_name)
    return f"Processed data from {api_name}"

@shared_task
def fetch_all_data():
    """
    Celery task to fetch and store data from all configured APIs.

    Returns:
        dict: A dictionary mapping each API source to its processing result.
    """
    logger.info("Starting fetch_all_data task")
    results = {}
    for api_name in ["products", "users", "transactions"]:
        result = fetch_and_store_data(api_name)
        results[api_name] = result
    logger.info("Completed fetch_all_data task with results: %s", results)
    return results
