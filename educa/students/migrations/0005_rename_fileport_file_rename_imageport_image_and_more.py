# Generated by Django 5.0.9 on 2024-11-15 11:25

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0004_rename_port_content_portcontent"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="FilePort",
            new_name="File",
        ),
        migrations.RenameModel(
            old_name="ImagePort",
            new_name="Image",
        ),
        migrations.RenameModel(
            old_name="TextPort",
            new_name="Text",
        ),
        migrations.RenameModel(
            old_name="VideoPort",
            new_name="Video",
        ),
    ]
