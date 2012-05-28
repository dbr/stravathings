function load_gpx(xml){
    var points = [];

    $(xml).find("trkpt").each(function(){
        points.push({'lat': $(this).attr("lat"),
                     'lon': $(this).attr("lon"),
                     'ele': $(this).find("ele").text(),
                     'time': $(this).find("time").text()});
    });

    return {"track": points,
            "time": $(xml).find("metadata").find("time").text()};
}

function write_gpx(gpx, opts){
    var xml = '<?xml version="1.0" encoding="UTF-8"?>';
    xml += '<gpx version="1.1" creator="strava.com" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">\n';

    xml += '  <metadata>\n';
    xml += '    <time>' + gpx['time'] + '</time>\n';
    xml += '  </metadata>\n';
    xml += '  <trk>\n';
    xml += '    <trkseg>\n';

    for(var i in gpx['track'])
    {

        if(i < opts['range'][0] || i > opts['range'][1])
        {
            xml += '      <trkpt lat="' + gpx['track'][i]['lat'] + '" lon="' + gpx['track'][i]['lon'] + '">\n';
            xml += '        <ele>' + gpx['track'][i]['ele'] + '</ele>\n';
            xml += '        <time>' + gpx['track'][i]['time'] + '</time>\n';
            xml += '      </trkpt>\n';
        }
    }

    xml += '    </trkseg>\n';
    xml += '  </trk>\n';
    xml += '</gpx>\n';

    return xml;
}

function track_to_latlngs(gpx)
{
    var ret = []
    for(i in gpx['track'])
    {
        ret.push(
            new google.maps.LatLng(gpx['track'][i]['lat'],
                                   gpx['track'][i]['lon']));
    }
    return ret;
}

function fitmap(map, points)
{
    // Zooms the given map to frame the supplied list of LatLng's
    var bounds = new google.maps.LatLngBounds();

    for (var i in points) {
        bounds.extend(points[i])
    };

    map.fitBounds(bounds);
}

function dim_map(map)
{
    var allcords = [
        [new google.maps.LatLng( - 85, 0.0), new google.maps.LatLng(85, 0.0), new google.maps.LatLng(85, 90), new google.maps.LatLng( - 85, 90)],
        [new google.maps.LatLng( - 85, 90), new google.maps.LatLng(85, 90), new google.maps.LatLng(85, 180), new google.maps.LatLng( - 85, 180)],
        [new google.maps.LatLng( - 85, 180.000001), new google.maps.LatLng(85, 180.000001), new google.maps.LatLng(85, 270), new google.maps.LatLng( - 85, 270)],
        [new google.maps.LatLng( - 85, 270), new google.maps.LatLng(85, 270), new google.maps.LatLng(85, 360), new google.maps.LatLng( - 85, 360)],
    ];

    for (var i in allcords)
    {
        bgpoly = new google.maps.Polygon({
            paths: allcords[i],
            strokeColor: "#fff",
            strokeOpacity: 0.9,
            strokeWeight: 1.0,
            fillColor: "#000",
            fillOpacity: 0.7,
            zIndex: -999999
        });
        bgpoly.setMap(map);
    }
}


var map;

$(function(){
    $("#map_canvas").hide();


    $("#makethinggo").click(function(){
        // Load map
        $("#map_canvas").show();

        map = new google.maps.Map(
            document.getElementById("map_canvas"),
            {
                zoom: 12,
                center: new google.maps.LatLng(0, 0),
                mapTypeId: google.maps.MapTypeId.ROADMAP
            }
        );


        // Load track
        var gpx = load_gpx($("#gpx_in").val());

        // Draw line on map
        var points = track_to_latlngs(gpx);
        fitmap(map, points);

        var Path = new google.maps.Polyline({
            clickable: false,
            geodesic: true,
            path: points,
            strokeColor: "rgb(1, 20, 255)",
            strokeOpacity: 0.500000,
            strokeWeight: 3,
            map: map
        });


        // Create slider to trim
	    var trim_slider = $("#slider-range").slider({
		    range: true,
		    min: 0,
		    max: points.length-1,
		    values: [0, points.length-1],
		    slide: function(event, ui) {
			    marker_start.setPosition(points[ui.values[0]]);
			    marker_end.setPosition(points[ui.values[1]]);
		    }
	    });


        // Add start/end region marker
	    var marker_start = new google.maps.Marker({
	        position: points[0],
	        map: map,
	        title:"Start"
	    });

	    var marker_end = new google.maps.Marker({
	        position: points[points.length-1],
	        map: map,
	        title:"End"
	    });

        $("#makecutgo").click(function(){
            console.log("Yay!");
            var trimmed_str = write_gpx(gpx, {range: $("#slider-range").slider("values")});
            $("#gpx_out").val(trimmed_str);
        });

    });

});
