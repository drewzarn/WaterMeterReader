<?php
require('config.php');
$window = array_key_exists('window', $_REQUEST) && is_int($_REQUEST['window']) ? $_REQUEST['window'] : 30;
$windowStart = time() - $window;
$sql = "SELECT * FROM ac_data WHERE ac_time>{$windowStart} ORDER BY ac_time ASC";

switch ($_REQUEST['a']) {
    case 'data':
        $result = $DB->query($sql);
        $liveSeries = [];
        while ($row = $result->fetch()) {
            $rowData = json_decode($row["ac_data"], true);
            for ($i = 0; $i < count($rowData['t']); $i++) {
                if(strpos($rowData['t'][$i], '.') === false) {
                    $rowData['t'][$i] .= '.0';
                }
                $dt = DateTime::createFromFormat('U.u', $rowData['t'][$i]);
                if (!$dt instanceof DateTime) {
                    ob_start();
                    var_dump($rowData['t'][$i], $dt);
                    error_log(ob_get_clean());
                }
                $dt->setTimezone(new DateTimeZone('America/Denver'));
                $liveSeries[] = [
                    'name' => $dt->format('H:i:s.v'),
                    'value' => $rowData['d'][$i]
                ];
            }
        }

        echo json_encode([['name' => 'Live', 'series' => $liveSeries]]);
        break;
}
