
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


class PredictionResult(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=EPA_PREDICTION_TITLE_LENGTH)
    result = models.ImageField(upload_to=EPA_PREDICTION_FOLDER)
    cells = models.FloatField()
    futureDate = models.DateField()

    def __unicode__(self):
        return self.title


class AggregateData(models.Model):
    average_cell = models.IntegerField()
    recent_event = models.IntegerField()
    highest_level_cell = models.IntegerField()
    normalized_index = models.IntegerField()
    change_history_chart = models.ImageField(upload_to='aggregate/')
    last_year_chart = models.ImageField(upload_to='aggregate/')
    change_history_data = models.CharField(max_length=500, null=True, blank=True)
    last_year_data = models.CharField(max_length=500, null=True, blank=True)

    def __unicode__(self):
        return u'Aggregate Data'


class ExecutePrediction(models.Model):
    prediction_point = models.CharField(max_length=EPA_EXECUTE_LENGTH)

    def __unicode__(self):
        return u'Execution Prediction Algorithm'


class PredictionAlgorithmConfiguration(models.Model):
    number_images = models.PositiveIntegerField()
    interval = models.PositiveIntegerField()
    prediction_point = models.CharField(max_length=EPA_EXECUTE_LENGTH)

    def __unicode__(self):
        return u'Prediction Algorithm Configuration'


#Models bellow managed by backend

class Notification(models.Model):
    subject = models.CharField(max_length=100, db_column='Subject')
    message = models.CharField(max_length=2000, db_column='Message')
    date_sent = models.DateTimeField(db_column='DateSent')

    def __unicode__(self):
        return self.date_sent

    class Meta:
        managed = False
        db_table = 'Notification'


class PredictionPoint(models.Model):
    point = models.CharField(max_length=200, db_column='Point')

    def __unicode__(self):
        return u'Prediction Point'

    class Meta:
        managed = False
        db_table = 'PredictionPoint'


class PredictionRequest(models.Model):
    date_requested = models.DateTimeField(db_column='DateRequested')
    date_fulFilled = models.DateTimeField(db_column='DateFulfilled', null=True)

    def __unicode__(self):
        return u'Prediction Result'

    class Meta:
        managed = False
        db_table = 'PredictionRequest'


class AlgorithmConfiguration(models.Model):
    number_of_images = models.PositiveIntegerField(db_column='MaxImageCount')
    interval = models.PositiveIntegerField(db_column='Days')
    point = models.CharField(max_length=200, db_column='Point')

    def __unicode__(self):
        return u'Algorithm Configuration'

    class Meta:
        managed = False
        db_table = 'AlgorithmConfiguration'


class DataManagementTrigger(models.Model):
    url = models.CharField(max_length=2000, db_column='Url')
    request_date = models.DateTimeField(db_column='RequestDate')

    def __unicode__(self):
        return u'Data Management Trigger'

    class Meta:
        managed = False
        db_table = 'DataManagementTrigger'
