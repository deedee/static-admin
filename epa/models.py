
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from EPA_Admin.settings import EPA_SHARED_FOLDER_DATA, EPA_SHARED_FOLDER, EPA_UPLOAD_DATA_FOLDER, MEDIA_ROOT, \
    EPA_UPLOAD_DATA_FILE_NAME_LENGTH, EPA_UPLOAD_DATA_THUMB_FOLDER, EPA_DEFAULT_THUMB_TXT_PATH, \
    EPA_DEFAULT_THUMB_IMAGE_PATH, EPA_THUMB_SIZE, EPA_HELP_CAT_LENGTH, EPA_HELP_TOPIC_LENGTH, \
    EPA_PREDICTION_FOLDER, EPA_PREDICTION_TITLE_LENGTH, EPA_EXECUTE_LENGTH
import datetime
import os
import string
import logging
import Image

logger = logging.getLogger(__name__)


class OverwriteStorage(FileSystemStorage):
    """
    Custum Storage. Django default storage never delete updated/deleted files.
    This storage is to make sure that all uploaded file is same file(and filename)
    with the original file
    """

    def _save(self, name, content):
        """
        Override the _save method
        """
        if self.exists(name):
            self.delete(name)
        return super(OverwriteStorage, self)._save(name, content)

    def get_available_name(self, name):
        return name


class UploadData(models.Model):
    FILE_TYPE = ((0, 'Image'), (1, 'Text'))
    file = models.FileField(upload_to=EPA_UPLOAD_DATA_FOLDER, storage=OverwriteStorage())
    thumbnail = models.ImageField(upload_to=EPA_UPLOAD_DATA_THUMB_FOLDER, blank=True, null=True)
    file_name = models.CharField(max_length=EPA_UPLOAD_DATA_FILE_NAME_LENGTH)
    user = models.ForeignKey(User, blank=True, null=True)
    date = models.DateTimeField(default=datetime.datetime.now())
    type = models.IntegerField(choices=FILE_TYPE)

    def __unicode__(self):
        return self.file_name

    def save(self, *args, **kwargs):
        """
        Custom save method.

        This will override the default save() to generate other field i.e thumbnail
        """
        super(UploadData, self).save(*args, **kwargs)
        try:
            thumb_name = ''
            thumb_path = ''
            if self.type == 0:
                thumb = Image.open(self.file.path)
                thumb.thumbnail(EPA_THUMB_SIZE, Image.ANTIALIAS)
                list_thumb_name = self.file_name.split('.')
                list_thumb_name.pop()
                thumb_name = string.join(list_thumb_name, '')
                thumb_path = MEDIA_ROOT + '/' + EPA_UPLOAD_DATA_THUMB_FOLDER + thumb_name + '_thumb.jpg'
                thumb.save(thumb_path, 'JPEG')

            else:
                thumb_name = 'default_text'
                thumb_path = EPA_DEFAULT_THUMB_TXT_PATH
            new_thumb = File(open(thumb_path, 'r'))
            self.thumbnail.save(thumb_name + '_thumb.jpg', new_thumb, save=False)
            super(UploadData, self).save(*args, **kwargs)
        except:
            if self.type == 0:
                thumb_name = 'default_image'
                thumb_path = EPA_DEFAULT_THUMB_IMAGE_PATH
            else:
                thumb_name = 'default_text'
                thumb_path = EPA_DEFAULT_THUMB_TXT_PATH
            new_thumb = File(open(thumb_path, 'r'))
            self.thumbnail.save(thumb_name + '_thumb.jpg', new_thumb, save=False)
            super(UploadData, self).save(*args, **kwargs)
            logger.error('UploadData.save(): failed to create thumbnail')


@receiver(models.signals.pre_delete, sender=UploadData)
def delete_signal(sender, instance, **kwargs):
    """
    Permanently delete file on fs on delete operation
    """
    if instance.file:
        try:
            #os.remove(EPA_SHARED_FOLDER + '/' + instance.file.name)
            os.remove(instance.file.path)
            _fname = instance.thumbnail.path.split('/')
            fname = _fname[len(_fname) - 1]
            if not fname[:7] == 'default':
                os.remove(instance.thumbnail.path)
        except:
            logger.error('UploadData.delete(): failed to delete file from shared folder')
            #raise OperationalError


class HelpCategory(models.Model):
    name = models.CharField(max_length=EPA_HELP_CAT_LENGTH)

    def __unicode__(self):
        return self.name


class HelpTopic(models.Model):
    title = models.CharField(max_length=EPA_HELP_TOPIC_LENGTH)
    content = models.TextField()
    category = models.ForeignKey(HelpCategory)

    def __unicode__(self):
        return self.title
