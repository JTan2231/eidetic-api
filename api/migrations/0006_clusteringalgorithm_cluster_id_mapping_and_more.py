# Generated by Django 4.1.5 on 2023-02-03 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_clusteringalgorithm'),
    ]

    operations = [
        migrations.AddField(
            model_name='clusteringalgorithm',
            name='cluster_id_mapping',
            field=models.BinaryField(default=b'0'),
        ),
        migrations.AlterModelTable(
            name='clusteringalgorithm',
            table='clustering_algorithms',
        ),
    ]
