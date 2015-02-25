<span class="belka">&nbsp Highcharts<span class="okno">

<script type="text/javascript" src="modules/kwh/html/js/jquery.min.js"></script>
<script src="modules/kwh/html/js/highstock.js"></script>
<script src="modules/kwh/html/js/exporting.js"></script>
<script type="text/javascript" src="modules/highcharts/js/dark-unica.js"></script>

<div id="container" style="height: 400px; min-width: 310px"></div>

<script type="text/javascript">



$(function () {
    var seriesOptions = [],
        seriesCounter = 0,
<?php
$ar=array();
$g=scandir('tmp/highcharts/');
foreach($g as $x)
{
    if(is_dir($x))$ar[$x]=scandir($x);
    else
	if (strpos($x,'system') !== false) {
		$rest1=str_replace(".json", "", "$x");
		$rest=str_replace("system_", "", "$rest1");
		$php_array[]=$rest;
		
	}
}
$js_array = json_encode($php_array);
echo "names = ". $js_array . ";\n";
?>
	

        // create the chart when all data is loaded
        createChart = function () {

            $('#container').highcharts('StockChart', {

		chart: {
            spacingBottom: 50
	    },


	legend: {
	enabled: true,
	floating: true,
        verticalAlign: 'bottom',
	align: 'center',
	y:40,
    	labelFormatter: function() {
                var lastVal = this.yData[this.yData.length - 1];
                    return '<span style="color:' + this.color + '">' + this.name + ': </span> <b>' + lastVal + '%</b> </n>';
    	    }
	},

	 rangeSelector: {
	inputEnabled: $('#container').width() > 480,
	selected: 0,
	buttons: [{
	type: 'hour',
	count: 1,
	text: '1h'
	},
	{
	type: 'day',
	count: 1,
	text: '1d'
	}, {
	type: 'day',
	count: 7,
	text: '7d'
	}, {
	type: 'month',
	count: 1,
	text: '1m'
	}, {
	type: 'ytd',
	text: 'YTD'
	}, {
	type: 'year',
	count: 1,
	text: '1y'
	}, {
	type: 'all',
	text: 'All'
	}]
	},


                yAxis: {
                    labels: {
                    },
                    plotLines: [{
                        value: 0,
                        width: 2,
                        color: 'silver'
                    }]
                },

                plotOptions: {
                    series: {
                    }
                },

                tooltip: {
                    pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b>%<br/>',
                    valueDecimals: 2
                },

                series: seriesOptions
            });
        };

    $.each(names, function (i, name) {

        $.getJSON('tmp/highcharts/system_' + name + '.json',    function (data) {
        
            seriesOptions[i] = {
                name: name,
                data: data
            };

            // As we're loading the data asynchronously, we don't know what order it will arrive. So
            // we keep a counter and create the chart when all the data is loaded.
            seriesCounter += 1;

            if (seriesCounter === names.length) {
                createChart();
            }
        });
    });
});
</script>

</span>
</span>