# Generated by Django 4.1.7 on 2023-03-06 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='bookAmount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True, verbose_name='账面金额'),
        ),
    ]