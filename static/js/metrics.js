var palette = new Rickshaw.Color.Palette();

var metrics_list = [];

var shared_graph;

function clearGraph() {
  $('#legend').empty();
  $('#chart_container').html('<div id="chart"></div><div id="timeline"></div><div id="legend_container"><div id="smoother" title="Smoothing"></div><div id="legend"></div></div><div id="slider"></div>');
  shared_graph = undefined;
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
    console.log(res);
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
                data['stats'] = parseTimestamps(
                    data['stats'],
                    data['absolute_values'],
                    data['unit_of_measure'],
                    data['time_unit']
                );

                var metrics = {
                    color: palette.color(),
                    data: data['stats'],
                    name: data['metric_name']
                };

                metrics_list.push(metrics);

                var graph = new Rickshaw.Graph( {
                    element: document.getElementById('chart'),
                    renderer: 'line',
                    height: 300,
                    series: [metrics]
                });

                if (shared_graph != undefined){
                    for (i in metrics_list){
                        shared_graph.series[i] = metrics_list[i];
                    }
                    while (shared_graph.series.length > metrics_list){
                        shared_graph.series.pop();
                    }
                    shared_graph.update();
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
                    element: document.querySelector('#legend')
                });

                var shelving = new Rickshaw.Graph.Behavior.Series.Toggle({
                    graph: graph,
                    legend: legend
                });

                var highlighter = new Rickshaw.Graph.Behavior.Series.Highlight({
                    graph: graph,
                    legend: legend
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
