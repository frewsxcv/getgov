# Generated by Django 4.2.1 on 2023-06-01 19:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registrar", "0023_alter_contact_first_name_alter_contact_last_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contact",
            name="email",
            field=models.EmailField(
                blank=True, db_index=True, help_text="Email", max_length=254, null=True
            ),
        ),
    ]
