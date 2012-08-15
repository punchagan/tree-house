$(document).ready( function () {
  var fetch = $('<a>').attr('id', 'fetch-button').attr('class', 'btn btn-primary btn-small')
    .text('Fetch Co-ordinates').click(address_to_coordinates);
  // FIXME: Add a spinner kinda thing, when geocoding is happening...
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
  var geocoder = new google.maps.Geocoder();
  var street = $('#field-address #address').val();
  var city = $('#field-city #city').val();

  var address = street+", "+city
  console.log("Geocoding:", address);

  if (geocoder) {
    geocoder.geocode({ 'address': address }, function (results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        var location = results[0].geometry.location;
        var lat = location.lat();
        var lng = location.lng();
        var url = "https://maps.google.com/maps?q="+lat+",+"+lng;
        $('#field-latitude #latitude').val(lat);
        $('#field-longitude #longitude').val(lng);
      }
      else {
        console.log("Geocoding failed: " + status);
      }
    });
  }
}
