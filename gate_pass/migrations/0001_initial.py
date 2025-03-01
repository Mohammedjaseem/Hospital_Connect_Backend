# Generated by Django 5.1.5 on 2025-02-13 12:46

import django.db.models.deletion
import utils.multis3
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('staff', '0006_alter_staffprofile_gender'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostelStaffGatePass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_on', models.DateTimeField(auto_now_add=True)),
                ('purpose', models.CharField(default='Purpose not mentioned', max_length=3000)),
                ('requesting_date', models.DateField(blank=True, null=True)),
                ('requesting_time', models.TimeField(blank=True, null=True)),
                ('return_date', models.DateField(null=True, verbose_name='Returning Date')),
                ('return_time', models.TimeField(blank=True, null=True)),
                ('pass_token', models.CharField(max_length=1560, unique=True)),
                ('request_status', models.CharField(default='Requested', max_length=200)),
                ('mentor_updated', models.BooleanField(blank=True, null=True)),
                ('updated_on', models.DateTimeField(blank=True, null=True, verbose_name='Mentor Update On')),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='GatePass/qrCodes/%Y/%m/%d/', verbose_name=utils.multis3.TenantMediaStorage())),
                ('qr_code_url', models.CharField(blank=True, max_length=1560, null=True)),
                ('remarks', models.TextField(blank=True, default='No remarks added !', null=True)),
                ('informed_warden', models.BooleanField(default=False)),
                ('gatepass_no', models.CharField(blank=True, max_length=50, null=True)),
                ('checked_out', models.BooleanField(default=False)),
                ('date_time_exit', models.DateTimeField(blank=True, null=True, verbose_name='Check Out')),
                ('checked_in', models.BooleanField(default=False)),
                ('date_time_entry', models.DateTimeField(blank=True, null=True, verbose_name='Check In')),
                ('duration', models.DurationField(blank=True, null=True)),
                ('mentor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gatepass_mentor', to='staff.staffprofile', verbose_name='mentor_warden')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_gatepasses', to='staff.staffprofile', verbose_name='Staff')),
            ],
            options={
                'verbose_name': 'Hostel Staff Gatepass',
                'verbose_name_plural': 'Hostel Staff Gatepass',
            },
        ),
    ]
