# Generated by Django 5.1.5 on 2025-02-13 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0007_staffprofile_hostel'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffprofile',
            name='room_no',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
