# Generated by Django 4.2.6 on 2024-01-24 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0002_user_email_is_verified"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="login_attempts",
            field=models.IntegerField(default=0),
        ),
    ]