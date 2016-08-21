$(function () {
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
