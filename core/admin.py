from django.contrib import admin
from .models import UserProfile, Category, Product, Transaction, APIRequestLog, APIDataCache,UnifiedEntity
from django.utils.timezone import now
from django.contrib import messages
from core.fetch_data import fetch_data_from_api
from core.services import transform_data, store_transformed_data

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'country', 'registered_date')
    search_fields = ('name', 'email')
    list_filter = ('country', 'registered_date')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'external_id')
    search_fields = ('title', 'external_id')
    list_filter = ('category',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'amount', 'timestamp')
    search_fields = ('user__name', 'product__title', 'external_id')
    list_filter = ('timestamp',)

@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'request_method', 'response_status', 'response_time', 'created_at')
    search_fields = ('endpoint', 'response_status')
    list_filter = ('response_status', 'created_at')

@admin.register(APIDataCache)
class APIDataCacheAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'fetched_at')
    search_fields = ('endpoint',)
    list_filter = ('fetched_at',)


@admin.action(description="Fetch & Process API Data")
def fetch_and_store_api_data(modeladmin, request, queryset):
    """
    Admin action to fetch, transform, and store API data.
    """
    api_names = ["products", "users", "transactions"]
    success_count = 0

    for api_name in api_names:
        raw_data = fetch_data_from_api(api_name)
        if raw_data:
            transformed_data = transform_data(api_name, raw_data)
            store_transformed_data(transformed_data)
            success_count += 1

    messages.success(request, f"Successfully fetched & processed {success_count} APIs.")


@admin.register(UnifiedEntity)
class UnifiedEntityAdmin(admin.ModelAdmin):
    list_display = ('entity_id', 'entity_type', 'timestamp', 'metadata', 'created_at')
    actions = [fetch_and_store_api_data]
    list_filter = ('entity_type', 'timestamp')
    search_fields = ('entity_id', 'entity_type')
    ordering = ('-timestamp',)


