# Generated by Django 5.1.6 on 2025-03-10 09:28

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_unifiedentity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apidatacache',
            name='endpoint',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='apirequestlog',
            name='request_method',
            field=models.CharField(choices=[('GET', 'GET'), ('POST', 'POST')], max_length=6),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='external_id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='unifiedentity',
            name='metadata',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='external_id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='registered_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
