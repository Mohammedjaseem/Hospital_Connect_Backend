import utils.multis3
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_rename_is_teaching_staff_staffprofile_is_hosteller'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffprofile',
            name='picture',
            field=models.ImageField(
                blank=True, 
                null=True, 
                storage=utils.multis3.TenantMediaStorage(), 
                upload_to="users/picture"  # Corrected upload_to
            ),
        ),
    ]
