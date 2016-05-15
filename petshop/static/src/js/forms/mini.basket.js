$.fn.miniBasket = function(){
    var miniBasket = this,
        id = miniBasket.attr('id'),
        link = $("[data-target=#" + id + "]"),
        navBar = $("#navbar"),
        clickOutside = function(evt){
            var target = $(evt.target);
            if(!target.closest('#' + id + ',[data-target=#' + id + ']').length){
                hideMiniBasket();
            }
        }
        hideMiniBasket = function(){
            miniBasket.find('.collapse').collapse('hide');
        },
        showMiniBasket = function(){
            miniBasket.find('.collapse').collapse('show');
        },
        bindForm = function(){
            miniBasket.find("form[data-type=ajax]").each(function(_, form){
                    $(form).ajaxForm();
                    $(form).on('submitSuccess', submitSuccess);
                    $(form).on('submitBefore', 
                    function(){
                        miniBasket.addClass("loading");
                });
            });
            miniBasket.find("form[data-type=ajax]")
            $("body").on("click", clickOutside);
        },
        updateContent = function(content){
            miniBasket.html(content);
            showMiniBasket();
            bindForm();
        },
        submitSuccess = function(evt, data){
            miniBasket.html(data.content);
            miniBasket.removeClass("loading");
            bindForm();
        };
    $(window).on("resize", function(evt){
        if(miniBasket.hasClass('in')){
            hideMiniBasket();
            showMiniBasket();
        }
    });
    $("body").on("click", "a[data-target=#" + id + "]", function(event){
        var link = $(this),
            url = link.data('url'),
            csrftoken = getCookie('csrftoken') || miniBasket.data('csrftoken');
        miniBasket.addClass("loading");
        $.ajax({
            url: url,
            type: 'post',
            data: {
                quantity: 1
            },
            error: function(){
                miniBasket.removeClass("loading");
            },
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).success(function(response){
            miniBasket.removeClass("loading");
            updateContent(response.content);
            $("html,body").animate({
                scrollTop: miniBasket.offset().top
            }, 400);
        });
        event.preventDefault();
    });
    bindForm();
    miniBasket.data('updateContent', updateContent);
    miniBasket.data('loading', function(state){
        if(state){
            miniBasket.addClass("loading");
        }
        else {
            miniBasket.removeClass("loading");
        }
    });
    return miniBasket;
}

$(function(){
    $("#miniBasket").miniBasket();
});
