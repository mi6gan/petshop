$(function(){
    var basketForm, checkoutForm,
        summaryBlock = $("#basketSummary"),
        initForms = function() {
            var totalSumCnt = $("#totalSum"),
                initialSum = totalSumCnt.data("initial"),
                currency = totalSumCnt.data("currency"),
                basketForm = $("#basketForm"),
                basketFormControls = $('input,button'),
                basketFormSubmitOnChangeTriggers = basketForm.find('[data-submitonchange]'),
                checkoutForm = $("#checkoutForm");
            basketForm.ajaxForm();
            checkoutForm.ajaxForm();
            basketFormSubmitOnChangeTriggers.on("change", function(){
                var trigger = $(this),
                    value = trigger.data('value')||this.defaultValue;
                basketForm.one(
                'submitBefore', function(){
                    basketFormControls.prop('disabled', true);
                }).one(
                'submitSuccess',
                function(){
                   basketFormControls.prop('disabled', false);
                   trigger.data('value', value);
                }).one(
                'submitError', 
                function(){
                   basketFormControls.prop('disabled', false);
                   trigger.val(value);
                }).trigger('submit');
            });
            basketForm.one("submitSuccess", onBasketSuccess);
            checkoutForm.on("submitSuccess", function(evt, response){
                document.location.href = response.success_url;
            });
            checkoutForm.find("input[type=radio][name=shippingform-method_code]").on("change", function(){
                var input = $(this),
                    extra = input.data("extra"),
                    shippingMethod = extra[this.value],
                    prefix = input.data('addressformprefix')||'',
                    charge = shippingMethod.charge;
                if(charge!=undefined){
                    totalSumCnt.text([(initialSum + charge), currency].join(" "));
                }
                checkoutForm.find("[name^=" + prefix + "-]").not("[type=hidden]").each(function(__, fieldEl){
                    var field = $(fieldEl);
                    if(shippingMethod.address.indexOf(fieldEl.name.replace(prefix + "-", ""))>-1){
                        if(field.data("initial")){
                            field.val("");
                            field.closest(".form-group").removeClass("hide");
                        }
                    } else {
                        field.val(field.data("initial"));
                        field.closest(".form-group").addClass("hide");
                    }
                });
            });//.trigger("change");
        },
        onBasketSuccess = function(evt, response) {
            summaryBlock.html(response.content);
            initForms();
        };
    initForms();
});
