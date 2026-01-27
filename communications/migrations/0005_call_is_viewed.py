# Generated migration for missed call view tracking

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communications', '0004_call_recording_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='is_viewed',
            field=models.BooleanField(default=False, help_text='Whether the missed call has been viewed by receiver'),
        ),
    ]
