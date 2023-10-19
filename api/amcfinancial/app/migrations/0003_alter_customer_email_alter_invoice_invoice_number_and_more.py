# Generated by Django 4.2.6 on 2023-10-15 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_user_id_access_history_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_number',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='user_root',
            name='email_Root',
            field=models.EmailField(max_length=255, unique=True),
        ),
    ]
