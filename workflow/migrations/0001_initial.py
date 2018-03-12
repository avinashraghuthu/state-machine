# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2018-03-12 20:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='StateCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=255)),
                ('destination_state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination', to='workflow.State')),
                ('source_state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source', to='workflow.State')),
            ],
        ),
        migrations.CreateModel(
            name='WorkflowInfo',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('initial_state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='initial_state', to='workflow.State')),
                ('state_conditions', models.ManyToManyField(related_name='state_conditions', to='workflow.StateCondition')),
                ('states', models.ManyToManyField(related_name='states', to='workflow.State')),
            ],
        ),
    ]
