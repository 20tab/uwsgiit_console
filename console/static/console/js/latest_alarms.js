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
                    var notification = new Notification('New alarm!', {'icon': 'icon.png', 'body': data[i]['msg']});
                    notification.onclick = function() {
                        window.location = alarm_url;
                    }
                    i++;
                }
            },
            complete: function() {
                setTimeout(get_latest_alarms, 180000);
            }
        });
    }

    get_latest_alarms();
}
