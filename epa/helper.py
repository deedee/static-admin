
from epa.exceptions import PersistenceError

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