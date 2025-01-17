# Generated by Django 4.1.5 on 2023-01-25 17:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registrar", "0008_remove_userprofile_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="domainapplication",
            name="federally_recognized_tribe",
            field=models.BooleanField(
                help_text="Is the tribe federally recognized", null=True
            ),
        ),
        migrations.AddField(
            model_name="domainapplication",
            name="state_recognized_tribe",
            field=models.BooleanField(
                help_text="Is the tribe recognized by a state", null=True
            ),
        ),
        migrations.AddField(
            model_name="domainapplication",
            name="tribe_name",
            field=models.TextField(blank=True, help_text="Name of tribe", null=True),
        ),
    ]
