# Generated by Django 3.2.12 on 2022-04-01 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_auto_20210602_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='followup',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='ticketduplicate',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='uservotelog',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]