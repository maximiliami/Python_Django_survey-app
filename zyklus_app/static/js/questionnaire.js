// prevents the browser from going back to the previous page

$(document).ready(function () {
    test()
});

function test() {
    $('.question_header').click(function (){
        let id = $(this).attr('id')
        $('#to_toggle_' + id).toggle('slow')

        $('#to_toggle_class_' + id).toggleClass('up').toggleClass('down')
    })
}