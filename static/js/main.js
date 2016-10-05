$(function () {
    var maxFileInPage = parseInt($($($('.pcNumber select')[0]).find('option:selected')[0]).text());

    $('#fileupload').fileupload({

        // This function is called when a file is added to the queue
        autoUpload: false,
        url: '/upload/',
        add: function (e, data) {
            var t = '<tr class="template-upload ">' +
                '<td><p class="name"></p><strong class="error text-danger"></strong></td><td><p class="size right"></p></td>' +
                '<td><div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="300" aria-valuenow="0"><div class="progress-bar progress-bar-success" style="width:0%;"></div></div>' +
                '</td><td>' +
                '<button class="btn btn-primary start hide" >' +
                '<i class="glyphicon glyphicon-upload"></i>' +
                '</button><button class="btn btn-warning cancel " >' +
                '<i class="glyphicon glyphicon-ban-circle"></i><span>Cancel</span>' +
                '</button></td></tr>';

            acceptFileTypes = /(\.|\/)(gif|jpe?g|png|bmp|plain|tiff|csv|ms-excel|sheet)$/i;
            maxFileSize = 0;
            $.each(data.files, function (i, p) {
                var ti = $(t).clone();
                ti.find('.name').text(p.name);
                ti.find('.size').text(p.size/1000 + ' KB');
                errorDesc = '';
                if(p['type'].length && !acceptFileTypes.test(p['type'])) {
                    errorDesc += 'file type is not allowed'
                }
                if(p['size'] && p['size'] > maxFileSize && maxFileSize > 0) {
                    if (errorDesc.length > 0){
                        errorDesc += ', ';
                    }
                    errorDesc += 'filesize is too big';
                }
                if(errorDesc.length > 0) {
                    ti.find('.error').text(errorDesc);
                    ti.delay(10000).fadeOut();
                }else{
                    $('button[type="submit"].start').removeAttr('disabled');
                    $('button[type="reset"].cancel').removeAttr('disabled');
                    ti.find('.start').on('click', function () {
                        var xhr = data.submit();
                        data.context.data('data', {jqXHR: xhr});
                    });
                    ti.find('.cancel').on('click', function () {
                        var template = $(this).closest('.template-upload');
                        data = template.data('data') || {};
                        if (!data.jqXHR){
                            template.remove();
                        }else{
                            data.jqXHR.abort();
                        }

                    });
                }
                ti.append('<input type="hidden" value="' + p.name + '" />');
                data.context = ti.appendTo('tbody');
            });
        },
        done: function (e, data) {
            var t = '<li class="fileBox"><div class="delFile"><span class="fLink">X</span></div>' +
                '<div class="imgFile"><span class="fLink"></span>' +
                '</div><div class="fileProp"><span class="fileName"></span><br />' +
                'Uploaded by <span class="name"><span class="fLink"></span></span><br />' +
                '</div></li>'
            $.each(data.result, function () {
                $('tbody input[value="' + this.name + '"]').closest('tr').fadeOut().remove();
                if (maxFileInPage > fileInThisPage) {
                    var ti = $(t).clone()
                    ti.find('.delFile .fLink').on('click',function () {
                        prepareDeleteFile(this);
                    }).append('<input type="hidden" name="id" value="' + this.id + '" />');
                        ti.find('.imgFile .fLink').on('click', function () {
                            showImage(this);
                        })
                            .append('<img src="' + this.thumbnail_url + '" />')
                            .append('<input type="hidden" name="iurl" value="' + this.url + '">')
                            .append('<input type="hidden" name="type" value="' + this.type + '">');
                    if (this.name.length > 17){
                        _name = this.name.substring(0,14) + '...'
                    }else{
                        _name = this.name
                    }
                    ti.find('.fileName').append(_name);
                    ti.find('.name .fLink').on('click', function () {
                        showUserProfile(this, false);
                    })
                        .append(this.user)
                        .append('<input type="hidden" name="email" value="' + this.email + '" />');
                    ti.find('.fileProp').append(this.date);
                    ti.appendTo('ul#grid');
                    ++fileInThisPage;
                }else{
                    current_page = parseInt($('.pageNumber .current:first').text());
                    current_view = $('.pcNumber select').val();
                    if ($('.nNext').length<1){
                        $('<span class="nNext"><a href="/prediction_data/' + ++current_page + '/' + current_view + '"><img ' +
                            'src="/static/img/right.png"/></a></span>').appendTo('.pageNumber');
                    }
                }
            });
            if (!$('.paginationContainer').is(':visible')) {
                $('.paginationContainer').show();
                $('.noData').hide();
            }

        },
        fail: function (e, data) {
            if (typeof (data.files) != 'undefined'){
                $.each(data.files, function () {
                    $('tbody input[value="' + this.name + '"]').closest('tr').find('.text-danger').text('failed');
                    $('tbody input[value="' + this.name + '"]').closest('tr').delay(5000).fadeOut();
                });
            }else if(typeof (data.context) !='undefined'){
                $(data.context).remove();
            }
        },
        stop: function(e){
            if (e.isDefaultPrevented()) {
                return false;
            }
                var that = $(this).data('blueimp-fileupload') ||
                        $(this).data('fileupload'),
                    deferred = that._addFinishedDeferreds();
                $.when.apply($, that._getFinishedDeferreds())
                    .done(function () {
                        that._trigger('stopped', e);
                    });
                that._transition($(this).find('.fileupload-progress')).done(
                    function () {
                        $(this).find('.progress')
                            .attr('aria-valuenow', '0')
                            .children().first().css('width', '0%');
                        $(this).find('.progress-extended').html('&nbsp;');
                        deferred.resolve();
                    }
                );
            $('button[type="submit"].start').attr('disabled','disabled');
            $('button[type="reset"].cancel').attr('disabled','disabled');
        }
    });

    //load mock chart
    if (typeof data1 != 'undefined'){
        var options={
            xaxis: {
                mode: "time",
                timeformat: "%m/%d/%Y"
            }
        }
        $.plot("#firstChart", [ data1 ], options);
    }

    if (typeof fileInThisPage != 'undefined') {
        if (fileInThisPage == 0) {
            $('.paginationContainer').hide();
            $('.noData').showClass();
            $('.noData').show();
        }
    }
    $('.pcNumber select').on('change', function () {
        window.document.location = '/prediction_data/1/' + $(this).val() + '/'
    });

    $('button[type="submit"].start').attr('disabled','disabled');
    $('button[type="reset"].cancel').attr('disabled','disabled');

    $('.bulk').click(function () {
        if ($('.bulk').is(':checked')) {
            $('#fileupload').fileupload( 'option', 'sequentialUploads', false);
        } else {
            $('#fileupload').fileupload( 'option', 'sequentialUploads', true);
        }
    });
    $('.puClose, .puCancel').on('click', function () {
        closeDialog();
    });
    $('.delFile').on('click', function () {
        prepareDeleteFile(this);
    });

    $('input[name="iurl"]').closest('.fLink').on('click', function () {
        showImage(this);
    });
    $('.fileProp .name .fLink').on('click', function () {
        showUserProfile(this, false);
    });
    $('.iep .fLink').on('click', function () {
        showPopUp('.ep');
    });
    $('.iconf .fLink').on('click', function () {
        showPopUp('.conf');
    });
    $('.mNote .fLink').on('click', function () {
        showNotification();
    });
    $('.notification .puSave').on('click', function () {
        if ($('.sendNote input').val().trim() === '' || $('.sendNote textarea').val().trim() === ''){
            $('.notification .error').text('Title and describtion must be filled');
            return false;
        }
        $.ajax({
            url: '/notification/',
            type: 'POST',
            dataType: 'json',
            data: {"title": $('.sendNote input').val(),
                "content": $('.sendNote textarea').val()},
            success: function (data, status, xhr) {
                showDialog('Notification', 'send...', false);
            },
            error: function (xhr, status, err) {
                var body = $.parseJSON(xhr.responseText);
                showDialog('Notification', getErrorMesssage(body.messages), false);
            }
        });
    });
    $('.epEdit button').on('click', function () {
        $('.epEdit').hideClass();
        $('.epSave').showClass();
        $('.epInput').showClass();
        $('.epText').hideClass();
        window.epText = $('.epText').text();
    });
    $('.epSave .epCancel').on('click', function () {
        $('.epEdit').showClass();
        $('.epSave').hideClass();
        $('.epInput').hideClass();
        $('.epText').showClass();
    });
    $('.epSave .epSaveBtn').on('click', function () {
        $('.epEdit').showClass();
        $('.epSave').hideClass();
        $('.epInput').hideClass();
        $('.epText').showClass();
        $.ajax({
            url: '/prediction_param/',
            type: 'POST',
            dataType: 'json',
            data: {"prediction_point": $('.ep .epInput input').val()},
            success: function (data, status, xhr) {
                $('.epText').text($('.epInput input').val() + ' Day');
            },
            error: function (xhr, status, err) {
                var body = $.parseJSON(xhr.responseText);
                var old_ep = $('.epText').text();
                 $('.ep .epInput input').val(old_ep.substring(0,old_ep.length-4));
                showDialog('Error', getErrorMesssage(body.messages), false);
            }
        });

    });

    $('.ep .puSave').on('click', function () {
        $.ajax({
            url: '/execute_prediction/',
            type: 'POST',
            dataType: 'json',
            data: {"prediction_point": $('input[name=prediction_point]').val()},
            success: function (data, status, xhr) {
                closeDialog()
                showDialog('Execute', 'Prediction Algorithm has been submit to be Executed', false);
            },
            error: function (xhr, status, err) {
                closeDialog();
                $('.epInput input').val($('.epInput input').val());
                var body = $.parseJSON(xhr.responseText);
                showDialog('Execute', getErrorMesssage(body.messages), false);
            }
        });
    });

    $('.conf .puSave').on('click', function () {
        $.ajax({
            url: '/save_config/',
            type: 'POST',
            dataType: 'json',
            data: {"number_images": $('.conf input[name="number_images"]').val(),
                "interval": $('.conf input[name="interval"]').val(),
                "prediction_point": $('.conf input[name="prediction_point"]').val()
            },
            success: function (data, status, xhr) {
                closeDialog()
                showDialog('Save Configuration', 'Saved', false);
            },
            error: function (xhr, status, err) {
                closeDialog();
                var body = $.parseJSON(xhr.responseText);
                showDialog('Save Failed', getErrorMesssage(body.messages), false);
            }
        });
    });
    $('.accName').on('click', function () {
        showUserProfile(this, true);
    });
    $('.accDelete').on('click', function () {
        var id = $(this).closest('.accList').find('input[name="id"]').val();
        $('.dialogBox .puSave').off();
        $('.dialogBox .puSave').on('click', function () {
            $.ajax({
                url: '/account_delete/',
                type: 'POST',
                dataType: 'json',
                data: {'id': id},
                success: function (data, status, xhr) {
                    closeDialog();
                    showDialog('User', 'Deleted', false);
                    $('.accList input[name="id"][value="' + data.id + '"]').closest('.accList').fadeOut();
                },
                error: function (xhr, status, err) {
                    closeDialog();
                    var body = $.parseJSON(xhr.responseText);
                    showDialog('User', getErrorMesssage(body.messages), false);
                }
            });
            closeDialog();
        });
        showDialog('User', 'Do you want to delete this user?', true);
    });
    $('.editMyUser .puSave').on('click', function () {
        var user = {'id': $('.editMyUser input[name="eId"]').val(),
            'username': $('.editMyUser input[name="eUsername"]').val(),
            'password': $('.editMyUser input[name="ePassword"]').val(),
            'password2': $('.editMyUser input[name="ePassword2"]').val(),
            'email': $('.editMyUser input[name="eEmail"]').val()
        }
        $.ajax({
            url: '/account/my/',
            type: 'POST',
            dataType: 'json',
            data: user,
            success: function (data, status, xhr) {
                closeDialog();
                showDialog('User', 'Saved', false);
                var li = $('.accList input[name="id"][value="' + data.id + '"]').closest('.accList');
                li.find('input[name="email"]').val(data.email);
                li.find('.accName').text(data.username);
            },
            error: function (xhr, status, err) {
                closeDialog();
                var body = $.parseJSON(xhr.responseText);
                showDialog('User', getErrorMesssage(body.messages), false);
            }
        });
    });
    $('.editOtherUser .puSave').on('click', function () {
        var user = {'id': $('.editOtherUser input[name="eId"]').val(),
            'username': $('.editOtherUser input[name="eUsername"]').val(),
            'old_password': $('.editOtherUser input[name="eOldPassword"]').val(),
            'password': $('.editOtherUser input[name="ePassword"]').val(),
            'password2': $('.editOtherUser input[name="ePassword2"]').val(),
            'email': $('.editOtherUser input[name="eEmail"]').val()
        }
        if (parseInt(user.id) > 0) {
            iurl = '/account/change/';
            newUser = false;
        } else {
            iurl = '/account/add/';
            newUser = true;
        }
        $.ajax({
            url: iurl,
            type: 'POST',
            dataType: 'json',
            data: user,
            success: function (data, status, xhr) {
                closeDialog();
                showDialog('User', 'Saved', false);

                if (newUser) {
                    var newli = $('<div class="accList"><span class="fLink accName"></span><span>' +
                        '<input type="hidden" name="id" >' +
                        '<input type="hidden" name="email" ></span>' +
                        '<span class="right"><span class="fLink accDelete">Delete </span>|<span class="fLink accEdit">' +
                        'Edit</span> </span></div>');
                    newli.find('.accName').text(data.username);
                    newli.find('input[name="id"]').val(data.id);
                    newli.find('input[name="email"]').val(data.email);
                    newli.find('.accEdit').on('click', function () {
                            var user = {'id': $(this).closest('.accList').find('input[name="id"]').val(),
                                'username': $(this).closest('.accList').find('.accName').text(),
                                'email': $(this).closest('.accList').find('input[name="email"]').val()
                            }
                            if ($(this).closest('.accList').find('.error').length > 0) {
                                showEditUser(user, '.editOtherUser');
                            } else {
                                if (typeof isSuperUser != 'undefined') {
                                    if (isSuperUser) {
                                        showEditUser(user, '.editOtherUser');
                                    } else {
                                        showEditUser(user, '.editMyUser');
                                    }
                                } else {
                                    showEditUser(user, '.editMyUser');
                                }
                            }

                    });

                    newli.find('.accName').on('click', function () {
                            showUserProfile(this, true);
                    });
                    newli.find('.accDelete').on('click', function () {
                            var id = $(this).closest('.accList').find('input[name="id"]').val();
                            $('.dialogBox .puSave').off();
                            $('.dialogBox .puSave').on('click', function () {
                                $.ajax({
                                    url: '/account_delete/',
                                    type: 'POST',
                                    dataType: 'json',
                                    data: {'id': id},
                                    success: function (data, status, xhr) {
                                        closeDialog();
                                        showDialog('User', 'Deleted', false);
                                        $('.accList input[name="id"][value="' + data.id + '"]').closest('.accList').fadeOut();
                                    },
                                    error: function (xhr, status, err) {
                                        closeDialog();
                                        var body = $.parseJSON(xhr.responseText);
                                        showDialog('User', getErrorMesssage(body.messages), false);
                                    }
                                });
                                closeDialog();
                            });
                            showDialog('User', 'Do you want to delete this user?', true);
                    });

                    $('.accArea').append(newli);
                } else {
                    var li = $('.accList input[name="id"][value="' + data.id + '"]').closest('.accList');
                    li.find('input[name="email"]').val(data.email);
                    li.find('.accName').text(data.username);
                }
            },
            error: function (xhr, status, err) {

                closeDialog();
                var body = $.parseJSON(xhr.responseText);
                showDialog('User', getErrorMesssage(body.messages), false);
            }
        });
    });

    $('.accNew').on('click', function () {
        $('.editOtherUser').find('input[name="eId"]').val('0');
        $('.editOtherUser').find('input[name="eUsername"]').val('');
        $('.editOtherUser').find('input[name="eEmail"]').val('');
        $('.editOtherUser').find('input[name="ePassword"]').val('');
        $('.editOtherUser').find('input[name="ePassword2"]').val('');
        $('.editOtherUser .puTitleText').text('Add New User');
        $('.editOtherUser .puSave').text('Create');
        showPopUp('.editOtherUser');
    });

    $('.accEdit').on('click', function () {
        var user = {'id': $(this).closest('.accList').find('input[name="id"]').val().trim(),
            'username': $(this).closest('.accList').find('.accName').text().trim(),
            'email': $(this).closest('.accList').find('input[name="email"]').val().trim()
        }
        if ($(this).closest('.accList').find('.error').length > 0) {
            showEditUser(user, '.editOtherUser');
        } else {
            if (typeof isSuperUser != 'undefined') {
                if (isSuperUser) {
                    showEditUser(user, '.editOtherUser');
                } else {
                    showEditUser(user, '.editMyUser');
                }
            } else {
                showEditUser(user, '.editMyUser');
            }
        }

    });

    $('.userProfileEdit .puSave').on('click', function () {
        var username = $('.userProfileEdit .username').text().trim();
        closeDialog();
        $('.accArea .accName:contains("' + username + '")')
            .closest('.accList').find('.accEdit').trigger("click");

    });
    $('.sendNot2 .fLink').on('click',function(){
        showNotification();
    });
    $('.rerun .fLink').on('click',function(){
        showPopUp('.ep');
    });
    $('.forgot.fLink').on('click',function(){
       showPopUp('.emailForgot');
    });
    $('#prGraph').hideClass();
    $('.btnUpload').showClass();
    $('.btnUrl').hideClass();
    $('#prTable').showClass();
    $('#prTable .fLink').on('click', function () {
        $('#prGraph').showClass();
        $('#prTable').hideClass();
    });
    $('.fUrl').on('click', function(){
        $('.btnUpload').hideClass();
        $('.btnUrl').showClass();
        $('tbody.files').hideClass();
    });
    $('.btnUrlCancel').on('click', function(){
        $('.btnUpload').showClass();
        $('tbody.files').showClass();
        $('.btnUrl').hideClass();
    });
    $('.btnUrlSend').on('click', function(){
        $.ajax({
            url: '/send_url/',
            type: 'POST',
            dataType: 'json',
            data: { 'imagesLocationUrl': $('#txtUrl').val()},
            success: function (data, status, xhr) {
                $('.btnUpload').showClass();
                $('tbody.files').showClass();
                $('.btnUrl').hideClass();
                showDialog('URL', 'URL has been sent', false);
            },
            error: function (xhr, status, err) {
                var body = $.parseJSON(xhr.responseText);
                showDialog('Failed', getErrorMesssage(body.messages), false);
            }

        });
    });

    $('.emailForgot .puSave').on('click', function(){
        $.ajax({
            url: '/reset/',
            type: 'POST',
            dataType: 'json',
            data: { 'email': $('#emailForgotInput').val()},
            success: function (data, status, xhr) {
                showDialog('Password Reset', 'Your new password has been sent to your email', false);
            },
            error: function (xhr, status, err) {
                var body = $.parseJSON(xhr.responseText);
                showDialog('Failed', getErrorMesssage(body.messages), false);
            }

        });
    });
});
    jQuery.fn.center = function () {
        this.css("position", "absolute");
        this.css("top", Math.max(0, (($(window).height() - $(this).outerHeight()) / 2) +
            $(window).scrollTop()) + "px");
        this.css("left", Math.max(0, (($(window).width() - $(this).outerWidth()) / 2) +
            $(window).scrollLeft()) + "px");
        return this;
    }
    jQuery.fn.hideClass = function () {
        if (!this.hasClass('hide')) {
            this.addClass('hide');
        }
        return this;
    }
    jQuery.fn.showClass = function () {
        if (this.hasClass('hide')) {
            this.removeClass('hide');
        }
        return this;
    }
    var prepareDeleteFile = function (el) {
        var id = $(el).find('input').val();

        $('.dialogBox .puSave').off();
        $('.dialogBox .puSave').on('click', function () {
            deleteFile(id);
            closeDialog();
        });
        showDialog('File Delete...', 'Are you sure want to delete this file?', true);
    }
    var deleteFile = function (id) {
        $.ajax({
            url: '/delete/',
            type: 'POST',
            dataType: 'json',
            data: { 'id': id},
            success: function (data, status, xhr) {
                $('#grid input[name="id"][value="' + data[0].id + '"]').closest('li').delay(500).fadeOut();
                --fileInThisPage;
                 if (fileInThisPage == 0) {
                    $('.paginationContainer').hide();
                    $('.noData').showClass();
                    $('.noData').show();
                 }
            },
            error: function (xhr, status, err) {
                var body = $.parseJSON(xhr.responseText);
                showDialog('File', getErrorMesssage(body.messages), false);
            }

        });

    }

    var showImage = function (el) {
        var url = $(el).find('input[name="iurl"]').val();
        var type = parseInt($(el).find('input[name="type"]').val());
        if (type == 0){
            var tiffRegex= /(.tiff|.tif)$/i;
            if (tiffRegex.test(url)){
                window.location = url;
            }else{
                $('.previewImage .imagePlaceholder a').attr('href', url);
                $('.previewImage .imagePlaceholder img').attr('src', url);
                showPopUp('.previewImage');
            }
        }else{
            window.location = url;
        }
    }

    var showUserProfile = function (el, edit) {
        var username = $(el).text();
        var email = $(el).closest('.accList').find('input[name="email"]').val();
        $('.popUp .username').text(username);
        $('.popUp .email').text(email);
        if (edit) {
            showPopUp('.userProfileEdit');
        } else {
            showPopUp('.userProfile');
        }
    }
    var showNotification = function () {
        $('.notification input').val('');
        $('.notification textarea').val('');
        $('.notification .error').text('');
        showPopUp('.notification');
    }
    var showEditUser = function( user,el){
        $(el).find('input[name="eId"]').val(user.id);
        $(el).find('input[name="eUsername"]').val(user.username);
        $(el).find('input[name="eEmail"]').val(user.email);
        $('.editOtherUser .puTitleText').text('Edit User');
        $('.editOtherUser .puSave').text('Update');
        showPopUp(el);
    }


    var showPopUp = function (name) {
        $('.popUpBack').showClass();
        $('.popUpBack').show();
        $(name).hide();
        $(name).showClass();
        $(name).fadeIn();
        $(name).center();
    }

    var showDialog = function (title, message, cancel) {
        if (cancel) {
            $('.dialogBox .puTitleText').text(title)
            $('.dialogBox .message').html(message);
            showPopUp('.dialogBox');
        } else {
            $('.alertBox .puTitleText').text(title);
            $('.alertBox .message').html(message);
            showPopUp('.alertBox');
        }

    }
    var closeDialog = function () {
        $('.epInput').hideClass();
        $('.epText').showClass();
        $('.epSave').hideClass();
        $('.epEdit').showClass();

        $('.popUp').each(function () {
            $(this).fadeOut();
        });
        $('.popUpBack').hideClass();
    }

    var getErrorMesssage = function(errors){
        message = '';
        $.each(errors,function(){
            message += '<li>' + this + '</li>';
        });
        return '<ul>' + message + '</ul>';
    }

var csrftoken = $.cookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
