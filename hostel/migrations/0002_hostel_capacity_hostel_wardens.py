# Generated by Django 5.1.5 on 2025-02-13 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0001_initial'),
        ('staff', '0006_alter_staffprofile_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostel',
            name='capacity',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='hostel',
            name='wardens',
            field=models.ManyToManyField(blank=True, null=True, related_name='hostels', to='staff.staffprofile', verbose_name='Wardens'),
        ),
    ]
