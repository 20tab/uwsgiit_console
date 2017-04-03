    var csrftoken = $.cookie('csrftoken');
    var palette = new Rickshaw.Color.Palette();

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var metrics = [];
    var unit_of_measure;
    var time_unit;

    for (i in dates){
        $.ajax({
            type: 'POST',
            async: false,
            url: url,
            data: dates[i],
            dataType: 'json',
            success: function (data) {
                unit_of_measure = data['unit_of_measure'];
                time_unit = data['time_unit'];
                data['stats'] = combineMultipleMetrics(
                    data['stats'],
                    data['absolute_values'],
                    data['unit_of_measure'],
                    data['time_unit'],
                    data['average']
                );

                var returned_metrics = {
                    color: palette.color(),
                    stroke: 'rgba(0,0,0,0.15)',
                    data: data['stats'],
                    name: data['metric_name']
                };
                metrics.push(returned_metrics);
            },
            error: function(data) {
                console.log(data);
            }
        });
    }

    var graph = new Rickshaw.Graph({
        element: $('#chart-')[0],
        renderer: 'area',
        stroke: true,
        height: 300,
        series: metrics
    });

    graph.render();

    if (unit_of_measure == 'bytes'){
        unit_of_measure = 'MB';
    }

    generateGraphDetails(graph, time_unit, unit_of_measure, '#legend-');
