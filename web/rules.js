$( document ).ready(function() {
    $('#startsnapshot').click(() => {
        $.get('snapshot.php?start&name=' + $('#snapshot_name').val());
    });
});