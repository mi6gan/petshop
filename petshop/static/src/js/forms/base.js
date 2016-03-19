function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
}

if(!$.fn.ajaxForm){

(function(){

$.fn.ajaxForm = function(){
    var form = this,
        formEl = form.get(0),
        formId = this.attr('id'),
        confirmBeforeUnload = form.data('confirmbeforeunload'),
        submitAlways = form.data('submitalways'),
        successURL = form.data('successurl'),
        reloadOnSuccess = form.data('reloadonsuccess'),
        disableOnSuccess = form.data('disableonsuccess'),
        hideOnSuccess = form.data('hideonsuccess'),
        initiallySubmitted = form.data('initiallysubmitted')||false,
        submitButtons = form.find('[type=submit]'),
        //.data('loading-text', gettext('Loading...')).button('reset'),
        nonFieldErrorsWrapper = $('[data-form=' + formId + ']').has('[data-bind=nonfielderrors]'),
        nonFieldErrorsTo = nonFieldErrorsWrapper.find('[data-bind=nonfielderrors]'),
        successMessageWrapper = $('[data-form=' + formId + ']').has('[data-bind=successmessage]'),
        successMessageTo = successMessageWrapper.find('[data-bind=successmessage]'),
        responseWrappers = successMessageWrapper.add(nonFieldErrorsWrapper);
        showResponseMessages = function(wrapper, to, messages){
            if(wrapper.length&&to.length&&messages.length){
              wrapper.removeClass("hide");
              setTimeout(function(){
                wrapper.addClass("in");
                to.html(messages
                        .join('<br>')
                        .split('\n').join('<br>'));
                    $("body,html").animate({
                            scrollTop: wrapper.offset().top - 250 
                        }, 300);
                    }, 1);
            }
        },
        fadeOut = function(sel, done) {
            done = (done instanceof Function) ? done : function(){};
            if(!sel.hasClass('hide')&&sel.hasClass('in')) {
                sel.one('transitionend', function(){
                    sel.addClass('hide');
                    done();
                }).addClass("out").removeClass("in");
            }
            else {
                done();
            }
        };

    form.find(".form-group [data-field]").each(function(i, fieldEl){
        var field = $(fieldEl),
            formGroup = field.closest('.form-group'),
            controlFeedback = formGroup.find('.form-control-feedback');
        field.popover({
            html: true,
            content: function(){
                var errors = field.data('errors');
                if(errors instanceof Array) {
                    errors = errors.join("<br>").split("\n").join("<br>");
                }
                return errors;
            },
            trigger: 'manual'
        });
        field.data('hideErrors', function(){
            if(formGroup.hasClass('has-error')){
                var input = field.find('input,textarea');
                field.popover('hide');
                input.attr('placeholder', field.data('placeholder')||input.attr('placeholder'));
                input.val(field.data('value')||'');
                formGroup.removeClass('has-error');
                controlFeedback.removeClass('in').addClass('out');
            }
        });
        formGroup
            .find('input,textarea')
            .on('focus', function(){
                field.data('hideErrors')();
            });
    });
    form.find('[data-toggle="tooltip"]').tooltip();
    submitButtons.on('click', function(evt){
        if($(this).attr('name')) {
            form.append(
                $("<input type='hidden'>").attr({ 
                    name: $(this).attr('name'), 
                    value: $(this).attr('value')
                })
            );
        }
    });
    submitButtons.prop('disabled', false);
    var formAjaxSerializer = {
        submitted: initiallySubmitted,
        onSubmitError: function(data) {
            errors = data.errors;
            submitButtons.button('reset');
            // submitButtons.find('.glyphicon').removeClass('glyphicon-refresh-animate').removeClass('glyphicon-refresh');
            for(errorName in errors){
                if(errorName=='__all__'){
                    showResponseMessages(nonFieldErrorsWrapper, nonFieldErrorsTo, errors[errorName]);
                }
                else {
                    var fieldName = errorName,
                        fieldErrors = errors[errorName],
                        field = $(".form-group [data-field=" + fieldName + "]"),
                        formGroup = field.closest('.form-group'),
                        hasFeedback = (formGroup.filter('.has-feedback').length >= 1);
                        field.data('errors', fieldErrors);
                        formGroup.addClass('has-error');
                    if(hasFeedback){
                        var input = field.find('input,textarea'),
                            placeholder = input.attr('placeholder'),
                            error = fieldErrors[0];
                        formGroup
                            .find('.form-control-feedback')
                            .removeClass('out')
                            .addClass('in')
                            .addClass('glyphicon')
                            .addClass('glyphicon-warning-sign');
                        field.data('placeholder', placeholder);
                        field.data('value', input.val());
                        if(input.length){
                            input.attr('placeholder', (input.val()||placeholder) + " \u2014 " + error[0].toLowerCase() + error.slice(1));
                        }
                        input.val('');
                    }
                    else {
                        field.popover('show');
                    }
                }
            }
            formAjaxSerializer.submitErrors = errors;
            form.trigger("submitError",[errors]);
            formAjaxSerializer.submitErrorData = data;
        },
        onSubmitSuccess: function(data){
            var success_url = (successURL==undefined) ? data.success_url : successURL;
            formAjaxSerializer.submitted = !submitAlways;
            submitButtons.button('reset');
            var dispatch = function() {
                if(data.message) {
                    showResponseMessages(successMessageWrapper, successMessageTo, [data.message]);
                }
            };
            if(disableOnSuccess){
                submitButtons.prop('disabled', true);
            }
            if(hideOnSuccess){
                form.get(0).reset();
                fadeOut(form, dispatch);
            }
            else if(reloadOnSuccess){
                if(success_url!=undefined) {
                    document.location.href = success_url;
                }
                else {
                    form.get(0).reset();
                    document.location.reload();
                }
            }
            else {
                dispatch();
            }
            form.trigger("submitSuccess",[data]);
            formAjaxSerializer.submitSuccessData = data;
        },
        submit: function(){
            formAjaxSerializer.params = {
                url:form.attr('action'),
                type:(form.attr("method")||"GET").toUpperCase(),
                error: formAjaxSerializer.onSubmitError,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            };
            if(formEl.enctype&&formEl.enctype.toLowerCase()=="multipart/form-data") {
                formAjaxSerializer.params.data = new FormData(formEl);
                formAjaxSerializer.params.processData = false;
                formAjaxSerializer.params.contentType = false;
            }
            else {
                formAjaxSerializer.params.data = form.serializeArray();
            }
            if(!formAjaxSerializer.submitted){
                delete formAjaxSerializer.submitErrorData;
                delete formAjaxSerializer.submitSuccessData;
                formAjaxSerializer.submitted = !submitAlways;
                form.find(".form-group [data-field]").each(function(i, fieldEl){
                    $(fieldEl).data('hideErrors')();
                });
                form.trigger("submitBefore", [formAjaxSerializer.params]);
                submitButtons.addClass("loading");
                $.ajax(formAjaxSerializer.params).done(
                    function(response){
                        submitButtons.removeClass("loading");
                        if(response.result=='ok') {
                            formAjaxSerializer.onSubmitSuccess(response);
                        }
                        else {
                            formAjaxSerializer.onSubmitError(response);
                        }
                    });
            } 
            else {
                if(formAjaxSerializer.submitErrorData){
                    formAjaxSerializer.onSubmitError(formAjaxSerializer.submitErrorData);
                }
                else if(formAjaxSerializer.submitSuccessData){
                    formAjaxSerializer.onSubmitSuccess(formAjaxSerializer.submitSuccessData);
                }
           }
        },
        init: function() {
            var field;
            for(var fieldName in formEl){
                field = formEl[fieldName];
                if(field) {
                    field.onchange = function(){
                        formAjaxSerializer.submitted = false;
                    };
                }
            }
            if(confirmBeforeUnload) {
                document.body.onbeforeunload = function(){
                    var confirmationMessage = gettext('ATTENTION! There is still unsubmitted data in the form.')
                    if(!formAjaxSerializer.submitted) {
                        return confirmationMessage;
                    }
                };
            }
            form.on("submit", function(evt){
                evt.preventDefault();
                if(formAjaxSerializer.submitted){
                    return;
                }
                fadeOut(responseWrappers, function() {
                    $.when($(".form-group [data-field]").map(function(el) {
                        var d = $.Deferred(),
                            obj = $(el);
                        if(!obj.length){
                            return d.resolve(); 
                        }
                        else {
                            obj.one('hidden.bs.popover', function(){
                                obj.removeClass('has-error');
                                d.resolve();
                            }).popover('hide');
                        }
                        return d.promise;
                    })
                    ).then(function() {
                        formAjaxSerializer.submit();
                    });
                });
            });
        }
    };
    formAjaxSerializer.init();
    return this;
};

$(function(){
    $("form[data-type=ajax]").each(function(i, form){
        $(form).ajaxForm();
    });
});

})();

}
