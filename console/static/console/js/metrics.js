var monthNames = [ "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December" ];

var metrics = {};

function clearGraph(id) {
    $('#legend-' + id).empty();
    $('#chart_container-' + id).html(
        '<div id="chart-' + id + '"></div>\
        <div id="timeline-' + id + '"></div>\
        <div id="legend_container-' + id + '">\
            <div id="legend-' + id + '" class="legend-class"></div>\
        </div>');
    metrics[id] = undefined;
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

function generateGraphDetails(graph, time_unit, unit_of_measure, legend_id){

    var xFormatter = function(x){
        if (time_unit == 'hour'){
            if (x < 12) {
                return x + ' AM';
            }
            else{
                return x + ' PM';
            }
        }
        else if (time_unit == 'year'){
            return x + ' ' + monthNames[x];
        }
        else{
            return x;
        }
    };

    var yFormatter = function(y) {
        return Math.round(y*10000)/10000 + ' ' + unit_of_measure;
    };

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
}


function generateModal(id, modal_id, chart_id, legend_id, legend_container_id){
    var identifier = id + '-' + modal_id;
    var modal = '<button class="btn btn-primary btn-lg btn-modal" data-toggle="modal" data-target="#modal-' + identifier + '">Open Graph</button>\
    <div class="modal fade" id="modal-' + identifier + '" tabindex="-1" role="dialog" aria-labelledby="label-' + identifier + '" aria-hidden="true">\
        <div class="modal-dialog">\
            <div class="modal-content">\
                <div class="modal-header">\
                    <button type="button" class="close" data-dismiss="modal">\
                        <span aria-hidden="true">&times;</span>\
                        <span class="sr-only">Close</span>\
                    </button>\
                    <h4 class="modal-title" id="label-' + identifier + '">' + modal_id + '</h4>\
                </div>\
                <div class="modal-body" id="modal-body-' + identifier + '"></div>\
                <div class="modal-footer">\
                    <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>\
                </div>\
            </div>\
        </div>\
    </div>'

    $(legend_container_id).append(modal);
    $(chart_id).clone().appendTo('#modal-body-' + identifier);
    $(legend_id).clone().appendTo('#modal-body-' + identifier);
}

function generateOpenInNewPageButton(id, form_id, metric_url, date, legend_container_id){
    var identifier = 'form-' + id + '-' + form_id;
    var form = $('<form/>', {action: metric_detail_url, method: 'GET', target: '_blank', id: identifier, class: 'inline'}).appendTo(legend_container_id);
    $('<input/>', {type: "hidden", name: "metric_url", value: metric_url}).appendTo(form);
    $('<input/>', {type: "hidden", name: "metric_type", value: $('#' + id + '-metric-list').find('.active').find('a').html()}).appendTo(form);
    $('<input/>', {type: "hidden", name: "subject", value: subject}).appendTo(form);

    addDateAsHiddenInputToForm('#' + form.attr('id') , date);
    form.append('<button class="btn btn-primary btn-lg" type="submit">Open In a New Page</button>');
}

function addDateAsHiddenInputToForm(form_id, date){
    var input = $('<input/>', {type: 'hidden', name: 'date_list[]', 'value': date}).appendTo(form_id);
}
