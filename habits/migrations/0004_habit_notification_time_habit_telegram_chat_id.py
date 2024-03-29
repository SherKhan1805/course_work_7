# Generated by Django 4.2.10 on 2024-03-08 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0003_alter_habit_periodicity'),
    ]

    operations = [
        migrations.AddField(
            model_name='habit',
            name='notification_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата и время следующего оповещения'),
        ),
        migrations.AddField(
            model_name='habit',
            name='telegram_chat_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Telegram'),
        ),
    ]
