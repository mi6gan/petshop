$(function(){
    var form = $("#add_to_basket_form"),
        priceOutput = form.find('[data-src=price]'),
        childSelect = form.find("select#id_child_id");
    childSelect.on('change', function() {
        var option = childSelect.find('option:selected');
        priceOutput.text(option.data('price'));
    }).trigger('change');
});
