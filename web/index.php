<?php
require('config.php');
?>

<html>

<head>
    <title>Meters!</title>
    <script src="https://code.jquery.com/jquery-3.5.1.js" integrity="sha256-QWo7LDvxbWT2tbbQ97B53yJnYU3WhH/C8ycbRAkjPDc=" crossorigin="anonymous"></script>
    <script src="rules.js"></script>
</head>

<body>
    <div id="status">
    </div>

    <div id="snapshots">
        <input type="text" id="snapshot_name" /><button id="startsnapshot">Start Snapshot</button>
    </div>

    <div id="intervals">
        <?php
        $r = $DB->query("SELECT test_ac_time, COUNT(*) AS test_count FROM ac_interval_tests GROUP BY test_ac_time ORDER BY test_ac_time");
        while ($row = $r->fetch()) {
            echo date('c', $row['test_ac_time']) . '<br />';
        }
        ?>
    </div>

</body>

</html>