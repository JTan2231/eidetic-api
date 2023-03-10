# Generated by Django 4.1.5 on 2023-02-03 02:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_entrylink_remove_collectionentry_collection_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('cluster_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClusterLink',
            fields=[
                ('cluster_link_id', models.AutoField(primary_key=True, serialize=False)),
                ('cluster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.cluster')),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.entry')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
