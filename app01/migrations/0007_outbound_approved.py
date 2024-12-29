# Generated by Django 4.1.7 on 2023-03-11 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0006_alter_outbound_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='outbound',
            name='approved',
            field=models.SmallIntegerField(choices=[(0, '未审核'), (1, '已审核')], default=0, verbose_name='审核'),
            preserve_default=False,
        ),
    ]
