# Generated by Django 4.2.6 on 2024-01-05 01:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_invoice_scheduled_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='access_history',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='access_history',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.userprofile'),
        ),
    ]
