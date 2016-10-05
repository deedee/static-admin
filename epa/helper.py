
from epa.models import AlgorithmConfiguration, PredictionPoint, Notification, \
    PredictionRequest, DataManagementTrigger
from epa.exceptions import PersistenceError, RestServiceCallError

from django.db import transaction
from django.db.models import Q

from datetime import datetime
import json
import re


def file_checker(filename, list_ext):
    """
    file validator by its extension
    """
    ext = filename[-4:].lower()
    for ex in list_ext:
        if ext in ex:
            return True
    return False


def write_data(data, path, user):
    """
    Helper method to write data
    """
    try:
        f = open(path, 'w')
        f.write('date : ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
        f.write('create_by : ' + user + '\n\n')
        f.write('data : ' + json.dumps(data))
    except:
        return False
    finally:
        f.close()
    return True


@transaction.atomic
def save_notification(title, content):
    """
    Helper to save notification
    """
    if not title or not content:
        raise ValueError('title and content can not null or empty')
    if not title.strip() and not content.strip():
        raise ValueError('title and content can not null or empty')
    try:
        notification = Notification()
        notification.subject = title
        notification.message = content
        notification.date_sent = datetime.now()
        notification.save()
    except Exception as e:
        raise PersistenceError('Failed to save notifivation (db error):' + e.message)


@transaction.atomic
def save_execute_prediction(prediction_point_p):
    """
    Helper to save prediction request
    """
    if not prediction_point_p:
        raise ValueError('predition point can not null or empty')
    if not prediction_point_p.strip():
        raise ValueError('predition point can not null or empty')
    try:
        prediction_point = PredictionPoint(point=prediction_point_p)
        prediction_point.save()
        prediction_request = PredictionRequest(date_requested=datetime.now())
        prediction_request.save()
    except Exception as e:
        raise PersistenceError('Failed to save Execute Request:' + e.message)


@transaction.atomic
def save_configuration(number_of_images, interval, prediction_point):
    """
    Helper to save configuration algorithm
    """
    if not number_of_images or not interval or not prediction_point:
        raise ValueError('number_of_images, interval, prediction_point can not null')
    if number_of_images < 1 or interval < 1:
        raise ValueError('number_of_images and interval must positive integer')

    try:
        AlgorithmConfiguration.objects.all().delete()
        config = AlgorithmConfiguration()
        config.number_of_images = number_of_images
        config.interval = interval
        config.point = prediction_point
        config.save()
    except Exception as e:
        return PersistenceError('Failed to save configuration: ' + e.message)


def get_data_from_rest_service(url):
    """
    Helper to save upload image by url
    """
    if not url:
        raise ValueError('url can not null or empty')

    import requests

    try:
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            raise Exception()
    except Exception as e:
        raise RestServiceCallError('failed to call: ' + url + '\n' + str(e.message))
    return r.json()


@transaction.atomic
def upload_images(file_location_url):
    if not file_location_url:
        raise ValueError('url can not null or empty')

    try:
        dmt = DataManagementTrigger(url=file_location_url, request_date=datetime.now())
        dmt.save()
    except Exception as e:
        raise PersistenceError('Failed to save image url(db error)' + e.message)


def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    '''
    Splits the query string in individual keywords
    '''

    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    '''
    Returns a query, that is a combination of Q objects. That combination
    aims to search keywords within a model by testing the given search fields.
    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def log_entrace(logger, *args):
    '''
    Logging Entrace helper
    '''
    func_input = ""
    for arg in args:
        func_input += str(arg) + ","
    func_input = func_input.rstrip(",")

    logger.debug("ENTRACE with input:" + func_input)


def log_exit(logger, value=None):
    '''
    logging Exit
    '''

    logger.debug("EXIT with return val" + str(value))