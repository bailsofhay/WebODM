# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-30 15:41
from __future__ import unicode_literals

from django.db import migrations, models
import uuid, os

from webodm import settings

tasks = []
imageuploads = []
task_ids = {} # map old task IDs --> new task IDs

def task_path(project_id, task_id):
    return os.path.join(settings.MEDIA_ROOT,
                        "project",
                        str(project_id),
                        "task",
                        str(task_id))

def rename_task_folders(apps, schema_editor):
    global tasks, task_ids

    for t in tasks:
        print("Checking task {}".format(t['id']))
        current_path = task_path(t['project'], t['id'])
        if os.path.exists(current_path):
            new_path = task_path(t['project'], task_ids[t['id']])
            print("Migrating {} --> {}".format(current_path, new_path))
            os.rename(current_path, new_path)


def create_uuids(apps, schema_editor):
    global tasks, task_ids

    Task = apps.get_model('app', 'Task')

    for task in tasks:
        # Generate UUID
        new_id = uuid.uuid4()

        # Save reference to it
        task_ids[task['id']] = new_id

        # Get real object from DB
        print(new_id)
        print(task)

        t = Task.objects.get(id=task['id'])
        t.new_id = new_id
        t.save()

    print("Created UUIDs")
    print(task_ids)

def restoreImageUploadFks(apps, schema_editor):
    global imageuploads, task_ids

    ImageUpload = apps.get_model('app', 'ImageUpload')
    Task = apps.get_model('app', 'Task')

    for img in imageuploads:
        i = ImageUpload.objects.get(pk=img['id'])
        print(task_ids)
        print(img)
        i.task = Task.objects.get(id=task_ids[img['task']])
        i.save()


def dump(apps, schema_editor):
    global tasks, imageuploads

    Task = apps.get_model('app', 'Task')
    ImageUpload = apps.get_model('app', 'ImageUpload')

    tasks = list(Task.objects.all().values('id', 'project'))
    imageuploads = list(ImageUpload.objects.all().values('id', 'task'))

    print("Dumped tasks and imageuploads in memory")


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20171109_1237'),
    ]

    operations = [
        migrations.RunPython(create_uuids),
        migrations.RunPython(rename_task_folders),

        migrations.AlterField(
            model_name='task',
            name='new_id',
            field=models.UUIDField(default=uuid.uuid4, unique=True, serialize=False, editable=False)
        ),
        migrations.RemoveField('task', 'id'),
        migrations.RenameField(
            model_name='task',
            old_name='new_id',
            new_name='id'
        ),
        migrations.AlterField(
            model_name='task',
            name='id',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, serialize=False, editable=False)
        ),

        migrations.AddField(
            model_name='imageupload',
            name='task',
            field=models.ForeignKey(null=True, on_delete=models.CASCADE, help_text="Task this image belongs to", to='app.Task')
        ),
        migrations.RunPython(restoreImageUploadFks),
        

    ]
