$(document).ready( function () {
  var fetch = $('<span>').attr('id', 'fetch-button').text('Fetch Lat/Lng').click(address_to_coordinates);
  // FIXME: Add a spinner kinda thing, when geocoding is happening...
  $(fetch).appendTo($('#field-city'));
  $('#field-latitude #latitude').attr('readonly', true);
  $('#field-longitude #longitude').attr('readonly', true);
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
        $('#map-url').text('Go there!').attr('href', url).attr('target', '_blank');
      }
      else {
        console.log("Geocoding failed: " + status);
      }
    });
  }
}
