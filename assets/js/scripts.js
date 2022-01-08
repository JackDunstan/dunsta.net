//makes background gradient follow cursor
$(document).mousemove(function(event) {
    windowWidth = $(window).width();
    windowHeight = $(window).height();

    mouseXpercentage = Math.round(event.pageX / windowWidth * 100);
    mouseYpercentage = Math.round(event.pageY / windowHeight * 100);

    $('.radial-gradient').css('background', 'radial-gradient(at ' + mouseXpercentage + '% ' + mouseYpercentage + '%, #2875a8, #714185)');
});
//tooltip
$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
});