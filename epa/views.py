
from django.shortcuts import render_to_response, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models.base import ObjectDoesNotExist, DatabaseError
from django.db import transaction
from django.core.exceptions import FieldError
from django.core.mail import send_mail
from epa.models import UploadData, HelpTopic, ExecutePrediction, \
    PredictionAlgorithmConfiguration, HelpCategory
from epa.forms import UploadDataForm, PredictionAlgorithmConfigurationForm, LoginForm, RegisterForm, \
    ExecutePredictionAlgorithmForm
from epa.exceptions import PersistenceError, RestServiceCallError
from epa import helper
from EPA_Admin.settings import EPA_FORGOT_PASSWORD_EMAIL_SENDER, EPA_FORGOT_PASSWORD_EMAIL_TITLE, \
    EPA_FORGOT_PASSWORD_EMAIL_BODY_TEMPLATE, EPA_DEFAULT_PASSWORD_LENGTH, GET_PREDICTION_RESULTS_URL, \
    GET_AGGREGATE_DATA_ANALYSIS_URL, EXECUTE_PREDICTION_DATA_ID, PREDICTION_ALGORITHM_CONFIG_DATA_ID
import json
import logging
import datetime

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['GET'])
def view_prediction_data(request, page=1, page_size=25):
    """
    View to handle prediction data page
    """
    helper.log_entrace(logger, request, page, page_size)

    uploaded = UploadData.objects.all()
    paginator = Paginator(uploaded, page_size)
    try:
        current_page = paginator.page(page)
    except (EmptyPage, InvalidPage) as e:
        logger.error('Error in method view_prediction_data:  ' + str(e.__class__) + e.message)
        current_page = paginator.page(paginator.num_pages)

    ep = ExecutePrediction.objects.get(pk=EXECUTE_PREDICTION_DATA_ID)
    pac = PredictionAlgorithmConfiguration.objects.get(pk=PREDICTION_ALGORITHM_CONFIG_DATA_ID)
    helper.log_exit(logger, 'view_prediction_data.html')

    return render_to_response('view_prediction_data.html', {'data': current_page,
                                                            'ep': ep,
                                                            'pac': pac,
                                                            'user': request.user})


@login_required
@require_http_methods(['POST'])
def upload_data(request):
    """
    View to handle file upload via ajax
    """
    helper.log_entrace(logger, request)
    if request.FILES is None:
        return HttpResponseBadRequest('Must have files attached!')

    uploaded_data = UploadData()
    upload_form = UploadDataForm(request.POST, request.FILES, instance=uploaded_data, request=request)
    result = []

    if upload_form.is_valid():
        try:
            upload_form.save()
        except FieldError as e:
            return HttpResponseBadRequest(json.dumps({'messages': [e.message]}))

        res = {"name": uploaded_data.file_name,
               "url": uploaded_data.file.url,
               "thumbnail_url": uploaded_data.thumbnail.url,
               "id": uploaded_data.id,
               "date": uploaded_data.date.strftime('%b %d, %Y'),
               "user": uploaded_data.user.username,
               "email": uploaded_data.user.email,
               "type": uploaded_data.type
               }
        result.append(res)
        return HttpResponse(json.dumps(result))
    else:
        logger.error('upload_data', upload_form)
        res = {"messages": ['Failed to upload file']}
        return HttpResponseBadRequest(json.dumps(res))


@login_required
@require_http_methods(['POST'])
def delete_data(request):
    """
    View to handle deleting data (image/text)
    """
    helper.log_entrace(logger, request)
    result = []
    try:
        id = int(request.POST.get('id', '0'))
    except ValueError as e:
        res = {"message": ['ID of file must supplied']}
        logger.error('Error in method delete_data:  ' + str(e.__class__) + e.message)
        return HttpResponseBadRequest(json.dumps(res))

    try:
        delete_data = UploadData.objects.get(pk=id)
        delete_data.delete()
    except (ObjectDoesNotExist, DatabaseError) as e:
        res = {"message": ['Object Not found or database error']}
        logger.error('Error in method view_prediction_data:  ' + str(e.__class__) + e.message)
        return HttpResponseNotFound(json.dumps(res))

    res = {"id": id}
    result.append(res)
    helper.log_exit(logger,res)
    return HttpResponse(json.dumps(result))




@login_required
@require_http_methods(['GET'])
def view_help(request, id=1):
    """
    View to handle help page

    """
    helper.log_entrace(logger,request,id)
    try:
        topic = HelpTopic.objects.get(pk=int(id))
    except (ValueError, ObjectDoesNotExist) as e:
        return HttpResponseBadRequest()
    categories = HelpCategory.objects.prefetch_related('helptopic_set').all().order_by('id')
    ep = ExecutePrediction.objects.get(pk=EXECUTE_PREDICTION_DATA_ID)
    return render_to_response('view_help.html', {'topic': topic,
                                                 'categories': categories,
                                                 'user': request.user,
                                                 'ep': ep})


@require_http_methods(['GET', 'POST'])
def view_login(request):
    """
    View to handle login

    """
    helper.log_entrace(logger,request)
    error = ''
    next = ''
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        next = request.POST.get('next', '/').strip()
        if not next:
            next = '/'
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next)
        else:
            form = LoginForm(request.POST)
            error = 'Invalid Username or Passwerd'
    else:
        if request.user.is_authenticated():
            return redirect('/')
        next = request.GET.get('next', '/').strip()
        form = LoginForm()
    has_user = False
    data = {'form': form, 'error': error,'has_user' : has_user,'next': next }
    data.update(csrf(request))
    return render_to_response('login.html', data)


@require_http_methods(['GET', 'POST'])
def register(request):
    """
    View to handle first time register page
    """
    helper.log_entrace(logger,request)
    if User.objects.all().count()>0:
        return redirect('/')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User()
            user.username = form.cleaned_data['username']
            user.set_password(form.cleaned_data['password'])
            user.email = form.cleaned_data['email']
            user.is_active = True
            user.is_superuser = False
            user.is_staff = True
            user.save()
            return redirect('/login/')
    else:
        form = RegisterForm()
    data = {'form': form}
    data.update(csrf(request))
    return render_to_response('register.html', data)


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(['GET'])
def view_user(request):
    """
    View to handle user management

    """
    helper.log_entrace(logger,request)
    users = User.objects.all()
    ep = ExecutePrediction.objects.get(pk=EXECUTE_PREDICTION_DATA_ID)
    return render_to_response('view_user.html', {'users': users, 'user': request.user,
                                                 'ep': ep})


@login_required
@require_http_methods(['POST', 'GET'])
def edit_user(request):
    """
    View to handle user edit

    """
    helper.log_entrace(logger,request)
    ep = ExecutePrediction.objects.get(pk=EXECUTE_PREDICTION_DATA_ID)
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        form.fields['password'].required = False
        form.fields['password2'].required = False
        form.new_user = False
        if form.is_valid():
            try:
                user = User.objects.get(pk=form.cleaned_data['id'])
                if not request.user.is_superuser and (not request.user.check_password(form.cleaned_data['old_password'])
                        or request.user.id != form.cleaned_data['id']):
                    data = {'form': form, 'error': "Password/Id didn't match",'user': request.user, 'ep': ep}
                    data.update(csrf(request))
                    return render_to_response('edit_user.html', data)
                user.username = form.cleaned_data['username']

                if len(form.cleaned_data['password']) > 0:
                    user.set_password(form.cleaned_data['password'])
                user.email = form.cleaned_data['email']
                user.save()
                if request.is_ajax():
                    return HttpResponse(json.dumps({'id': user.id,
                                         'username': user.username,
                                         'email': user.email
                                        }))
                else:
                    return redirect('/prediction_data/')
            except:
                return HttpResponseBadRequest(json.dumps({'messages': ['Fail to found account ID']}))
        else:
            if request.is_ajax():
                list_errors= []
                for f,errors in form.errors.items():
                    for e in errors:
                        list_errors.append(e)
                return HttpResponseBadRequest(json.dumps({'messages': list_errors}))
            else:
                error = 'Failed'
    else:
        data = {'id': request.user.id,
                'username': request.user.username,
                'email':request.user.email}
        form = RegisterForm(initial=data)
        error = ''
    dataForm = {'form': form, 'error': error,'user': request.user,'ep': ep}
    dataForm.update(csrf(request))

    return render_to_response('edit_user.html', dataForm)


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(['POST'])
def delete_user(request):
    """
    View to handle deleting user

    """
    helper.log_entrace(logger,request)
    try:
        id = int(request.POST.get('id','0'))
        user = User.objects.get(pk=id)
    except Exception as e:
        logger.error('Error in method delete_user:  ' + str(e.__class__) + e.message)
        return HttpResponseBadRequest(json.dumps({'messages': ['Failed to delete user']}))

    if user == request.user:
        return HttpResponseBadRequest(json.dumps({'messages': ['You can not delete yourself']}))

    user.delete()
    return HttpResponse(json.dumps({"id": id}))


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(['POST'])
def add_user(request):
    """
    View to handle add user

    """
    helper.log_entrace(logger,request)
    form = RegisterForm(request.POST)
    if form.is_valid():
        user = User()
        user.username = form.cleaned_data['username']
        user.set_password(form.cleaned_data['password'])
        user.email = form.cleaned_data['email']
        user.is_active = True
        user.is_superuser = False
        user.is_staff = False
        user.save()
        return HttpResponse(json.dumps({'id': user.id,
                                        'username': user.username,
                                        'email': user.email}))
    else:
        list_errors= []
        for f,errors in form.errors.items():
            for e in errors:
                list_errors.append(e)
        return HttpResponseBadRequest(json.dumps({'messages': list_errors}))


@require_http_methods(['POST'])
@transaction.atomic
def reset_password(request):
    """
    View to handle password reset
    """
    helper.log_entrace(logger,request)
    postEmail = request.POST.get('email', '')

    try:
        import socket

        user = User.objects.get(email = postEmail)
        import os, random, string

        chars = string.ascii_letters + string.digits
        random.seed = os.urandom(1024)

        new_password = ''.join(random.choice(chars) for i in range(EPA_DEFAULT_PASSWORD_LENGTH))
        user.set_password(new_password)

        try:
            send_mail(EPA_FORGOT_PASSWORD_EMAIL_TITLE, EPA_FORGOT_PASSWORD_EMAIL_BODY_TEMPLATE.replace('%username%', user.username)
                                    .replace('%new_password%', new_password), EPA_FORGOT_PASSWORD_EMAIL_SENDER, [user.email])
            user.save()
            return HttpResponse(json.dumps([{'status': 'ok'}]))
        except socket.error:
            return HttpResponseServerError(json.dumps({'messages': ['Fail while try connecting to mail server']}))

    except (ObjectDoesNotExist, DatabaseError) as e:
        res = {"messages": ['User Not found']}
        logger.error('Error in method view_prediction_data:  ' + str(e.__class__) + e.message)
        return HttpResponseNotFound(json.dumps(res))




@login_required
@require_http_methods(['POST'])
def upload_from_url(request):
    """
    View to handle upload image by url
    """
    helper.log_entrace(logger,request)
    url = request.POST.get('imagesLocationUrl', '')

    if len(url) > 2000:
        return HttpResponseBadRequest(json.dumps({'messages': ['Url must have at most 2000 characters']}))
    if not url.lower().startswith('ftp://'):
        return HttpResponseBadRequest(json.dumps({'messages': ['Only support fot FTP']}))
    try:
        helper.upload_images(url)
        return HttpResponse(json.dumps([{'status': 'ok'}]))
    except PersistenceError as e:
        logger.error('Error in method upload_from_url:  ' + str(e.__class__) + e.message)
        return HttpResponseServerError(json.dumps({'messages': [e.message]}))



@login_required
@require_http_methods(['GET'])
def search_help(request):
    '''
    search help view
    '''
    helper.log_entrace(logger,request)
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = helper.get_query(query_string, ['title', 'content',])

        found_entries = HelpTopic.objects.filter(entry_query)

    return render_to_response('search_help_results.html',
                          { 'query_string': query_string, 'entries': found_entries, 'user': request.user })
