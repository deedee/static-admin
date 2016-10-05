

from django.contrib import admin
from epa.models import *
# Register your models here.

admin.site.register(UploadData)
admin.site.register(HelpCategory)
admin.site.register(HelpTopic)
admin.site.register(PredictionResult)
admin.site.register(AggregateData)
admin.site.register(ExecutePrediction)
admin.site.register(PredictionAlgorithmConfiguration)