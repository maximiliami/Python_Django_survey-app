// prevents the browser from going back to the previous page
function preventBack(){
    window.history.forward();
}
setTimeout("preventBack()", 0);
window.onunload = function () {
    null
}