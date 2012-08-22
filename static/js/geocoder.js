$(document).ready( function () {
  var fetch = $('<a>').attr('id', 'fetch-button').attr('class', 'btn btn-primary btn-small')
    .text('Fetch Co-ordinates').click(address_to_coordinates);
  $(fetch).appendTo($('#field-city .controls'));
  var note = "Enter address & click Fetch co-ordinates";
  var $latitude = $('#field-latitude #latitude');
  $latitude.attr('readonly', true);
  if ($latitude.val() == '') {$latitude.val(note)};

  var $longitude = $('#field-longitude #longitude');
  $longitude.attr('readonly', true);
  if ($longitude.val() == '') {$longitude.val(note)};
  $('<a>').attr('id', 'map-url').insertAfter($(fetch));
});

var address_to_coordinates = function() {
  var geocoder = new google.maps.Geocoder(),
      street = $('#field-address #address').val(),
      city = $('#field-city #city').val(),
      latitude = $('#field-latitude #latitude'),
      longitude = $('#field-longitude #longitude'),
      address = street+", "+city;

  console.log("Geocoding:", address);

  latitude.val('Fetching...');
  longitude.val('Fetching...');

  if (geocoder) {
    geocoder.geocode({ 'address': address }, function (results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        var location = results[0].geometry.location;
        var lat = location.lat();
        var lng = location.lng();
        var url = "https://maps.google.com/maps?q="+lat+",+"+lng;
        latitude.val(lat);
        longitude.val(lng);
      }
      else {
        console.log("Geocoding failed: " + status);
        latitude.val('Failed!');
        longitude.val('Failed!');
      }
    });
  }
}
