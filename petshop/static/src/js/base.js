$(function toggleClass() {
    $("[data-toggle-class]").each(function (__, e) {
        var toggler = $(e),  
            className = toggler.data('toggle-class'),
            eventName = toggler.data('toggle-on'),
            target = toggler.parent(),
            targetName = toggler.data('toggle-target'); 
        if(targetName != 'parent') {
            target = target.find(targetName).eq(0);
        }
        switch(eventName) {
            case 'click':
                break;
            case 'mouseover':
                break;
            default:
                console.warn('usupported event ' + className + ' to trigger class');
                return;
        }
        toggler.on(eventName, function () {
            target.toggleClass(className);
        });
    });
});
$(function yandexMetrika() {
    if($(body).hasClass('debug') {
        return;
    }
    (function (d, w, c) {
        (w[c] = w[c] || []).push(function() {
            try {
                w.yaCounter39277665 = new Ya.Metrika({
                    id:39277665,
                    clickmap:true,
                    trackLinks:true,
                    accurateTrackBounce:true
                });
            } catch(e) { }
        });

        var n = d.getElementsByTagName("script")[0],
            s = d.createElement("script"),
            f = function () { n.parentNode.insertBefore(s, n); };
        s.type = "text/javascript";
        s.async = true;
        s.src = "https://mc.yandex.ru/metrika/watch.js";

        if (w.opera == "[object Opera]") {
            d.addEventListener("DOMContentLoaded", f, false);
        } else { f(); }
    })(document, window, "yandex_metrika_callbacks");
});
