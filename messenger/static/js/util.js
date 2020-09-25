// bootstrap modal open/close functions
function closeModal(id) {
    $('#' + id).modal('hide');
}
function openModal(id) {
    $('#' + id).modal({
        show: true
    });
}

/**
 * Returns the cookie with the given name
 *
 * If no cookie with the given name exists, null is returned.
 *
 * See: https://stackoverflow.com/a/22852843/2828700y
 * @param {string} c_name
 */
function getCookie(c_name) {
    var c_value = ' ' + document.cookie;
    var c_start = c_value.indexOf(' ' + c_name + '=');

    if (c_start == -1) {
        c_value = null;
    } else {
        c_start = c_value.indexOf('=', c_start) + 1;
        var c_end = c_value.indexOf(';', c_start);
        if (c_end == -1) {
            c_end = c_value.length;
        }
        c_value = unescape(c_value.substring(c_start, c_end));
    }

    return c_value;
}

function setElementText(elementId, text) {
    document.getElementById(elementId).innerHTML = text;
}

function clearNode(node) {
    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }
}

function reloadPage() {
    window.location.reload(false);
}