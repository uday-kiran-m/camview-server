# Generated by Django 3.2.7 on 2021-11-05 21:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='cams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('camname', models.CharField(max_length=50)),
                ('camstatus', models.BooleanField(default=False)),
                ('camdevice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpanel.devices')),
            ],
        ),
        migrations.AlterField(
            model_name='otp',
            name='cam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpanel.cams'),
        ),
    ]