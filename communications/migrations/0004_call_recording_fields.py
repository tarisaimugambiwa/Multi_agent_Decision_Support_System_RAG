# Generated migration for call recording fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communications', '0003_call_caller_offer_call_ice_candidates_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='connected_at',
            field=models.DateTimeField(blank=True, help_text='When both parties connected', null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='is_recording',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='call',
            name='recording_duration',
            field=models.IntegerField(blank=True, help_text='Recording duration in seconds', null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='recording_ended_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='recording_file_path',
            field=models.CharField(blank=True, help_text='Path to recording file', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='recording_started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='recording_url',
            field=models.URLField(blank=True, help_text='URL to access recording', null=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='status',
            field=models.CharField(
                choices=[
                    ('idle', 'Idle'),
                    ('initiated', 'Initiated'),
                    ('ringing', 'Ringing'),
                    ('connected', 'Connected'),
                    ('recording', 'Recording'),
                    ('ended', 'Ended'),
                    ('missed', 'Missed'),
                    ('declined', 'Declined'),
                ],
                default='initiated',
                max_length=20,
            ),
        ),
    ]
