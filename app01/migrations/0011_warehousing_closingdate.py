# Generated by Django 4.1.7 on 2023-03-23 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0010_outbound_batchcode_warehousing_batchcode_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehousing',
            name='closingDate',
            field=models.DateField(blank=True, null=True, verbose_name='截止日期'),
        ),
    ]