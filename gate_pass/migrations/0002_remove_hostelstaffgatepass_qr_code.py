# Generated by Django 5.1.5 on 2025-02-13 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gate_pass', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hostelstaffgatepass',
            name='qr_code',
        ),
    ]
