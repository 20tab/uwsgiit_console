function hexToRgb(hex) {
    // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
    var shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, function(m, r, g, b) {
        return r + r + g + g + b + b;
    });

    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}


if (("Notification" in window)) {
    var permission = Notification.permission;
    if (permission != "granted") {
        Notification.requestPermission(function (permission) {
            if (permission != "granted") {
                return false;
            }
        });
    }

    function get_latest_alarms() {
        $.ajax({
            type: 'GET',
            url: latest_alarms_url,
            dataType: 'json',
            success: function (data) {
                var i = 0;
                while (data[i]['id'] != last_alarm_id) {
                    color = hexToRgb(data[i]['color']);
                    var notification = new Notification('New alarm!', {'icon': '/gif_' +color.r+ '_' +color.g+ '_' +color.b+ '.gif', 'body': data[i]['msg']});
                    notification.onclick = function() {
                        window.location = alarm_url;
                    }
                    i++;
                }
                last_alarm_id = data[0]['id'];
            },
            complete: function() {
                setTimeout(get_latest_alarms, 180000);
            }
        });
    }

    get_latest_alarms();
}
