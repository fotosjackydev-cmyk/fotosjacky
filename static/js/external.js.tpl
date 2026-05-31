{# ===== External JS — jQuery Dependent ===== #}
{# Libraries that require jQuery to be loaded first #}
{# jQuery is loaded by Tienda Nube's platform #}

{# Cookie plugin for cart persistence #}
if (typeof jQueryNuvem !== 'undefined') {
    jQueryNuvem.cookie = function(name, value, options) {
        if (typeof value != 'undefined') {
            options = options || {};
            if (value === null) { value = ''; options.expires = -1; }
            var expires = '';
            if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
                var date;
                if (typeof options.expires == 'number') {
                    date = new Date();
                    date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
                } else { date = options.expires; }
                expires = '; expires=' + date.toUTCString();
            }
            document.cookie = [name, '=', encodeURIComponent(value), expires, options.path ? '; path=' + options.path : '', options.domain ? '; domain=' + options.domain : '', options.secure ? '; secure' : ''].join('');
        } else {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].replace(/^\s+/, '');
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    };
}
