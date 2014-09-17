var palette = new Rickshaw.Color.Palette();

var monthNames = [ "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December" ];

var metrics_list = {};

var shared_graphs = {};

var last_graphs_time_unit = {};

function clearGraph(id) {
    $('#legend-' + id).empty();
    $('#chart_container-' + id).html(
        '<div id="chart-' + id + '"></div>\
        <div id="timeline-' + id + '"></div>\
        <div id="legend_container-' + id + '">\
            <div id="legend-' + id + '" class="legend-class"></div>\
        </div>');
    shared_graphs[id] = undefined;
    last_graphs_time_unit[id] = undefined;
    metrics_list[id] = undefined;
    palette = new Rickshaw.Color.Palette();
}

function combineMultipleMetrics(list, absoluteValues, unitOfMeasure, timeUnit, calculateAverage){

    var data = {};

    for (i in list){
        var metric = parseTimestamps(list[i], absoluteValues, unitOfMeasure, timeUnit);
        for (j in metric){
            if(data[j] != undefined){
                data[j][0] += metric[j][0];
                data[j][1] += metric[j][1];
            }
            else{
                data[j] = metric[j];
            }
        }
    }
    var res = [];

    for(var el in data){
        if (calculateAverage){
            var value = data[el][0] / data[el][1];
        }
        else{
            var value = data[el][0];
        }
        res.push({x: parseInt(el), y: value});
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


function parseTimestamps(list, absoluteValues, unitOfMeasure, timeUnit){
    var data = {};

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
            date_value = date.getDate();
        }
        else if(timeUnit == 'month'){
            date_value = date.getMonth();
        }
        if(data[date_value] != undefined){
            data[date_value][0] += value;
            data[date_value][1] += 1;
        }
        else{
            data[date_value] = [value, 1];
        }
    }
    return data;
}

$(document).ready(function() {
    $('.get-metrics-btn').click(function () {
        var id = $(this).attr('data-id')
        $(this).button('loading');
        var frm = $('#calendar-' + id);
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            dataType: 'json',
            success: function (data) {
                if (data['metric_name'] == 'Invalid date'){
                    alert('Invalid date');
                    $('#get-metrics-' + id).button('reset');
                    return;
                }
                if (last_graphs_time_unit[id] != undefined && last_graphs_time_unit[id] != data['time_unit']){
                    clearGraph(id);
                }
                last_graphs_time_unit[id] = data['time_unit'];

                data['stats'] = combineMultipleMetrics(
                    data['stats'],
                    data['absolute_values'],
                    data['unit_of_measure'],
                    data['time_unit'],
                    data['average']
                );

                var metrics = {
                    color: palette.color(),
                    stroke: 'rgba(0,0,0,0.15)',
                    data: data['stats'],
                    name: data['metric_name']
                };
                if (metrics_list[id] == undefined){
                    metrics_list[id] = [];
                }
                metrics_list[id].push(metrics);

                if (data['unit_of_measure'] == 'bytes'){
                    data['unit_of_measure'] = 'MB';
                }

                var xFormatter = function(x){
                    if (data['time_unit'] == 'hour'){
                        if (x < 12) {
                            return x + ' AM';
                        }
                        else{
                            return x + ' PM';
                        }
                    }
                    else if (data['time_unit'] == 'year'){
                        return x + ' ' + monthNames[x];
                    }
                    else{
                        return x;
                    }
                };

                var yFormatter = function(y) {
                    return Math.round(y*10000)/10000 + ' ' + data['unit_of_measure']
                };


                var chart_id;
                var legend_id;
                var legend_container_id;

                if (shared_graphs[id] != undefined){
                    $('#chart_container-' + id).append(
                        '<div id="chart-' + id + '-' + data['metric_name'] + '"></div>\
                        <div id="timeline-' + id + '-' + data['metric_name'] + '"></div>\
                        <div id="legend_container-' + id + '-' + data['metric_name'] + '">\
                            <div id="legend-' + id + '-' + data['metric_name'] + '"></div>\
                        </div>'
                    );
                    chart_id = '#chart-' + id + '-' + data['metric_name'];
                    legend_id = '#legend-' + id + '-' + data['metric_name'];
                    legend_container_id = '#legend_container-' + id + '-' + data['metric_name'];

                }
                else{
                    chart_id = '#chart-' + id;
                    legend_id = '#legend-' + id;
                    legend_container_id = '#legend_container-' + id;
                }

                var graph = new Rickshaw.Graph({
                    element: $(chart_id)[0],
                    renderer: 'area',
                    stroke: true,
                    height: 300,
                    series: [metrics]
                });


                if (shared_graphs[id] != undefined){
                    for (i in metrics_list[id]){
                        shared_graphs[id].series[i] = metrics_list[id][i];
                    }
                    while (shared_graphs[id].series.length > metrics_list[id]){
                        shared_graphs[id].series.pop();
                    }
                    shared_graphs[id].update();
                    $('#legend-' + id).empty();
                    var shared_graphs_legend = new Rickshaw.Graph.Legend({
                        graph: shared_graphs[id],
                        element: $('#legend-' + id)[0]
                    });
                    var shared_graphs_shelving = new Rickshaw.Graph.Behavior.Series.Toggle({
                        graph: shared_graphs[id],
                        legend: shared_graphs_legend
                    });
                    var shared_graphs_highlighter = new Rickshaw.Graph.Behavior.Series.Highlight({
                        graph: shared_graphs[id],
                        legend: shared_graphs_legend
                    });
                }
                else{
                    shared_graphs[id] = graph;
                }

                graph.render();

                var hoverDetail = new Rickshaw.Graph.HoverDetail( {
                    graph: graph,
                    xFormatter: xFormatter,
                    yFormatter: yFormatter
                });

                var legend = new Rickshaw.Graph.Legend({
                    graph: graph,
                    element: document.querySelector(legend_id)
                });

                var xAxis = new Rickshaw.Graph.Axis.X( {
                  graph: graph,
                  orientation: 'top',
                  tickFormat: xFormatter,
                });
                xAxis.render();

                var yAxis = new Rickshaw.Graph.Axis.Y( {
                    graph: graph,
                    tickFormat: yFormatter,
                });
                yAxis.render();

                generateModal(id, data['metric_name'], chart_id, legend_id, legend_container_id);
                $('#get-metrics-' + id).button('reset');
            },
            error: function(data) {
                console.log('cane');
                console.log(data);
                $('#get-metrics-' + id).button('reset');
            }
        });
        return false;
    });
});


function generateModal(id, modal_id, chart_id, legend_id, legend_container_id){
    var modal = '<button class="btn btn-primary btn-lg btn-modal" data-toggle="modal" data-target="#modal-' + id + '-' + modal_id + '">Open Graph</button>\
    <div class="modal fade" id="modal-' + id + '-' + modal_id + '" tabindex="-1" role="dialog" aria-labelledby="label-' + modal_id + '" aria-hidden="true">\
        <div class="modal-dialog">\
            <div class="modal-content">\
                <div class="modal-header">\
                    <button type="button" class="close" data-dismiss="modal">\
                        <span aria-hidden="true">&times;</span>\
                        <span class="sr-only">Close</span>\
                    </button>\
                    <h4 class="modal-title" id="label-' + id + '-' + modal_id + '">' + modal_id + '</h4>\
                </div>\
                <div class="modal-body" id="modal-' + id + '-body-' + modal_id + '"></div>\
                <div class="modal-footer">\
                    <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>\
                </div>\
            </div>\
        </div>\
    </div>'

    $(legend_container_id).append(modal);
    $(chart_id).clone().appendTo('#modal-' + id + '-body-' + modal_id);
    $(legend_id).clone().appendTo('#modal-' + id + '-body-' + modal_id);
}
