$(document).ready(function() {
    $('.get-metrics-btn').click(function () {
        var id = $(this).attr('data-id');
        $(this).button('loading');
        var frm = $('#calendar-' + id);
        var frm_data = frm.serialize();
        var frm_action = frm.attr('action');
        $.ajax({
            type: frm.attr('method'),
            url: frm_action,
            data: frm_data,
            dataType: 'json',
            success: function (data) {
                if (data['metric_name'] == 'Invalid date'){
                    alert('Invalid date');
                    $('#get-metrics-' + id).button('reset');
                    return;
                }
                if (metrics[id] != undefined && metrics[id].date_list.indexOf(data['metric_name']) != -1 ){
                    alert('Graph already present');
                    $('#get-metrics-' + id).button('reset');
                    return;
                }

                data['stats'] = combineMultipleMetrics(
                    data['stats'],
                    data['absolute_values'],
                    data['unit_of_measure'],
                    data['time_unit'],
                    data['average']
                );

                var chart_id;
                var legend_id;
                var legend_container_id;

                if (metrics[id] == undefined || metrics[id].last_time_unit != data['time_unit']){
                    clearGraphs(id);
                    metrics[id] = {
                        last_time_unit: data['time_unit'],
                        // shared_graph: undefined,
                        metric_list: [],
                        form_id: undefined,
                        palette: new Rickshaw.Color.Palette(),
                        date_list: []
                    };

                    chart_id = '#chart-' + id;
                    legend_id = '#legend-' + id;
                    legend_container_id = '#legend_container-' + id;
                }
                else {
                    $('#chart_container-' + id).append(
                        '<div id="chart-' + id + '-' + data['metric_name'] + '"></div>\
                        <div id="legend_container-' + id + '-' + data['metric_name'] + '">\
                            <div id="legend-' + id + '-' + data['metric_name'] + '"></div>\
                        </div>'
                    );
                    chart_id = '#chart-' + id + '-' + data['metric_name'];
                    legend_id = '#legend-' + id + '-' + data['metric_name'];
                    legend_container_id = '#legend_container-' + id + '-' + data['metric_name'];
                }

                var attribute_value = frm_data.substring(frm_data.indexOf("&") + 1);
                metrics[id].date_list.push(data['metric_name']);

                var returned_metrics = {
                    color: metrics[id].palette.color(),
                    stroke: 'rgba(0,0,0,0.15)',
                    data: data['stats'],
                    name: data['metric_name']
                };

                metrics[id].metric_list.push(returned_metrics);

                if (data['unit_of_measure'] == 'bytes'){
                    data['unit_of_measure'] = 'MB';
                }

                var graph = new Rickshaw.Graph({
                    // width: 400,
                    height: 200,
                    element: $(chart_id)[0],
                    renderer: 'area',
                    stroke: true,
                    series: [returned_metrics]
                });


                // if (metrics[id].shared_graph != undefined){
                //     for (i in metrics[id].metric_list){
                //         metrics[id].shared_graph.series[i] = metrics[id].metric_list[i];
                //     }
                //     while (metrics[id].shared_graph.series.length > metrics[id].metric_list){
                //         metrics[id].shared_graph.series.pop();
                //     }
                //     metrics[id].shared_graph.update();
                //     $('#legend-' + id).empty();
                //     var shared_graphs_legend = new Rickshaw.Graph.Legend({
                //         graph: metrics[id].shared_graph,
                //         element: $('#legend-' + id)[0]
                //     });
                //     var shared_graphs_shelving = new Rickshaw.Graph.Behavior.Series.Toggle({
                //         graph: metrics[id].shared_graph,
                //         legend: shared_graphs_legend
                //     });
                //     var shared_graphs_highlighter = new Rickshaw.Graph.Behavior.Series.Highlight({
                //         graph: metrics[id].shared_graph,
                //         legend: shared_graphs_legend
                //     });
                //     addDateAsHiddenInputToForm(metrics[id].form_id, attribute_value);
                // }
                // else{
                //     metrics[id].shared_graph = graph;
                // }

                graph.render();

                generateGraphDetails(graph, data['time_unit'], data['unit_of_measure'], legend_id);
                // generateModal(id, data['metric_name'], chart_id, legend_id, legend_container_id);
                generateOpenInNewPageButton(id, data['metric_name'], frm_action, attribute_value, legend_container_id);
                // if (graph != metrics[id].shared_graph){
                generateCloseGraphButton(id, data['metric_name'], legend_container_id);
                // }
                if (metrics[id].form_id == undefined){
                    metrics[id].form_id = '#form-' + id + '-' + data['metric_name'];
                }
                $('#get-metrics-' + id).button('reset');
            },
            error: function(data) {
                console.log(data);
                $('#get-metrics-' + id).button('reset');
            }
        });
        return false;
    });
});
