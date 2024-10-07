function normalizeLatLng(latLng) {
    // Wrap longitude within [-180, 180]
    var lng = ((latLng.lng + 180) % 360 + 360) % 360 - 180;

    return L.latLng(latLng.lat, lng);
}
var map = L.map('map').setView([0, 0], 2);

L.tileLayer('https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
    subdomains: ['a', 'b', 'c']
}).addTo(map);

// Add a marker
var marker = L.marker([0, 0]).addTo(map);

// Update the marker position when the map is clicked
map.on('click', function(e) {
    marker.setLatLng(e.latlng);
    latlng = normalizeLatLng(e.latlng);
    document.getElementById('latitude').value = latlng.lat;
    document.getElementById('longitude').value = latlng.lng;
    $('#map_form').submit();
});

$(document).ready(function() {
    $('#map_form').on('submit', function(event) {
        event.preventDefault();

        const formData = {
            longitude: $('#longitude').val(),
            latitude: $('#latitude').val()
        };

        $.ajax({
            url: '/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                $('#selection_wrapper').html(response.img);
                $('#response').html(response.html);
            },
            error: function(error) {
                $('#response').html('<p>Error: ' + error.responseText + '</p>');
            }
        });
    });

    // Show the popup when a Notify Me! button is clicked
    $(document).on('click', '.popupButton', function(e) {
        e.preventDefault(); // Prevent default anchor behavior

        // Get the information from the clicked button
        var date = $(this).data('date'); // Assuming data-date attribute holds the date
        var satellite = $(this).data('satellite'); // Assuming data-satellite attribute holds the satellite name
        
        // Update the popup title with the information
        $('#notificationInfo').text(date + ' (' + satellite + ')');

        // Store data in hidden input
        $('#notificationInfo').data('date', date);
        $('#notificationInfo').data('satellite', satellite);
        $('#notificationInfo').data('latitude', latitude);
        $('#notificationInfo').data('longitude', longitude);
        
        $('#popup').show(); // Show the popup
    });

    // Close the popup when the close button is clicked
    $(document).on('click', '.close', function() {
        $('#popup').hide(); // Hide the popup
    });

    // Handle the submit action for the days input
    $('#notifySubmit').on('click', function() {
        var days = $('#days').val();
        var date = $('#notificationInfo').data('date');
        var satellite = $('#notificationInfo').data('satellite');
        var latitude = $('#notificationInfo').data('latitude');
        var longitude = $('#notificationInfo').data('longitude');

        if (days) {
            // Send AJAX request to handle the notification
            $.ajax({
                url: '/set_notification', // Update with your endpoint
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ 
                        days: days, 
                        date: date, 
                        satellite: satellite,
                        latitude: latitude,
                        longitude: longitude
                    }),
                    success: function(response) {
                        alert('Notification set for ' + days + ' days for ' + date + ' (' + satellite + ').');
                        $('#popup').hide(); // Hide the popup after successful submission
                    },
                error: function(error) {
                    alert('Error setting notification: ' + error.responseText);
                }
            });
        } else {
            alert('Please enter a valid number of days.');
        }
    });

    $(document).on('click', '.bands', function() {
        $('#radiobox-form').submit();
    });
    
    $(document).on('submit', '#radiobox-form', function(event) {
        event.preventDefault();  // Prevent the form from submitting the traditional way

        const formData = {
            long: $('#longitude').val(),
            lat: $('#latitude').val(),
            band: $('input[name="option"]:checked').val()
        };

        $('#img-grid').attr('src', '/plot.png?' + $.param(formData));
    });
});