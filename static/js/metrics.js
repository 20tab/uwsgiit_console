var palette = new Rickshaw.Color.Palette();

var metrics_list = [];

var shared_graph;

var last_graph_time_unit;

function clearGraph() {
    $('#legend').empty();
    $('#chart_container').html(
        '<div id="chart"></div>\
        <div id="timeline"></div>\
        <div id="legend_container">\
            <div id="smoother" title="Smoothing"></div>\
            <div id="legend"></div>\
        </div>\
        <div id="slider"></div>');
    shared_graph = undefined;
    last_graph_time_unit = undefined;
    metrics_list = [];
    palette = new Rickshaw.Color.Palette();
}


function parseTimestamps(list, absoluteValues, unitOfMeasure, timeUnit){
    var data = [];

    if (list.length < 2){
        return [];
    }

    for (var i = 1; i < list.length; i++){
        var date = new Date(list[i][0] * 1000);
        var value;
        if (absoluteValues){
            value = list[i][1]
        }
        else{
            value = list[i][1] - list[i-1][1];
            if (value < 0){
                value = list[i][1];
            }
        }
        if (unitOfMeasure == 'bytes'){
            value = value / (1024*1024);
        }

        var date_value;

        if (timeUnit == 'hour'){
            date_value = date.getHours();
        }
        else if(timeUnit == 'day'){
            date_value = date.getUTCDate();
        }
        else if(timeUnit == 'month'){
            date_value = date.getUTCMonth();
        }
        console.log(date.getMinutes(), date.getHours(), date.getUTCDate(), date.getUTCMonth());
        if(data[date_value] != undefined){
            data[date_value] += value;
        }
        else{
            data[date_value] = value;
        }
    }
    var res = [];
    for(var el in data){
        res.push({x: parseInt(el), y: data[el]});
    }

    var fixed_length;

    if (timeUnit == 'hour'){
        fixed_length = 24;
    }
    else if(timeUnit == 'day'){
        fixed_length = 31;
    }
    else if(timeUnit == 'month'){
        fixed_length = 12;
    }
    while(res.length < fixed_length){
        res.push({x: res.length, y: 0});
    }
    return res;
}


$(document).ready(function() {
    var frm = $('#calendar');
    frm.submit(function () {
        $('#get-metrics').button('loading');
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            dataType: 'json',
            success: function (data) {
                if (last_graph_time_unit != undefined && last_graph_time_unit != data['time_unit']){
                    clearGraph();
                }

                last_graph_time_unit = data['time_unit'];

                data['stats'] = parseTimestamps(
                    data['stats'],
                    data['absolute_values'],
                    data['unit_of_measure'],
                    data['time_unit']
                );

                var metrics = {
                    color: palette.color(),
                    stroke: 'rgba(0,0,0,0.15)',
                    data: data['stats'],
                    name: data['metric_name']
                };

                metrics_list.push(metrics);

                var chart_id;

                if (shared_graph != undefined){
                    $('#chart_container').append(
                        '<div id="chart-' + data['metric_name'] + '"></div>\
                        <div id="timeline-' + data['metric_name'] + '"></div>\
                        <div id="legend_container-' + data['metric_name'] + '">\
                            <div id="smoother-' + data['metric_name'] + '" title="Smoothing"></div>\
                            <div id="legend-' + data['metric_name'] + '"></div>\
                        </div>\
                        <div id="slider-' + data['metric_name'] + '"></div>'
                    );
                    chart_id = 'chart-' + data['metric_name'];
                    legend_id = '#legend-' + data['metric_name'];

                }
                else{
                    chart_id = 'chart';
                    legend_id = '#legend';
                }

                var graph = new Rickshaw.Graph({
                    element: document.getElementById(chart_id),
                    renderer: 'area',
                    stroke: true,
                    height: 300,
                    series: [metrics]
                });

                var legend_id;

                if (shared_graph != undefined){
                    for (i in metrics_list){
                        shared_graph.series[i] = metrics_list[i];
                    }
                    while (shared_graph.series.length > metrics_list){
                        shared_graph.series.pop();
                    }
                    shared_graph.update();
                    $('#legend_container').empty();
                    var shared_graph_legend = new Rickshaw.Graph.Legend({
                        graph: shared_graph,
                        element: document.getElementById('legend_container')
                    });
                    var shelving = new Rickshaw.Graph.Behavior.Series.Toggle({
                        graph: shared_graph,
                        legend: shared_graph_legend
                    });
                    var highlighter = new Rickshaw.Graph.Behavior.Series.Highlight({
                        graph: shared_graph,
                        legend: shared_graph_legend
                    });
                }
                else{
                    shared_graph = graph;
                }

                graph.render();

                var hoverDetail = new Rickshaw.Graph.HoverDetail( {
                    graph: graph,
                    xFormatter: function(x) {
                        return x;
                    }
                });

                var legend = new Rickshaw.Graph.Legend({
                    graph: graph,
                    element: document.querySelector(legend_id)
                });

                var timeFixture = new Rickshaw.Fixtures.Time();
                var timeUnit = timeFixture.unit(data['time_unit']);
                var xAxis = new Rickshaw.Graph.Axis.Time( {
                  graph: graph,
                  timeUnit: timeUnit,
                });
                xAxis.render();

                var yAxis = new Rickshaw.Graph.Axis.Y( {
                    graph: graph
                });
                yAxis.render();
                $('#get-metrics').button('reset');
            },
            error: function(data) {
                console.log(data);
                $('#get-metrics').button('reset');
            }
        });
        return false;
    });

});
