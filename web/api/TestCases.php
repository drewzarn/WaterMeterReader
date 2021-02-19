<?php
require('config.php');
$listSql = "SELECT snap_name, test_ac_time * 1000 AS test_ac_time, case_id, case_peak_height, case_peak_prominence, test_peak_count, test_peak_times, test_peak_intervals, test_interval_stats, test_avg_interval
    FROM ac_interval_tests
    JOIN ac_data ON ac_time=test_ac_time
    JOIN snapshots ON (
        snap_start_time BETWEEN ac_time and ac_end_time
        OR ac_time BETWEEN snap_start_time AND snap_end_time
        OR snap_end_time BETWEEN ac_time AND ac_end_time)
    JOIN peak_test_cases ON case_id=test_case_id
    ORDER BY ac_time ASC";

switch ($_REQUEST['a']) {
    case 'list':
        $result = $DB->query($listSql);
        $tests = [];
        while ($row = $result->fetch()) {
            $tests[] = $row;
        }
        echo json_encode($tests);
        break;
    case 'data':
        $entityBody = file_get_contents('php://input');
        $reqObj = json_decode($entityBody);
        $times = $reqObj->times;
        $epochTimes = [];
        foreach ($times as $time) {
            //Multiply the time by 1000 without multiplying it because floating points are stupid
            $timeLength = strlen($time);
            $decimalPos = strpos($time, '.');
            $timeArray = str_split($time);
            array_splice($timeArray, $decimalPos - 3, 0, '.');
            unset($timeArray[$decimalPos + 1]);
            $dbTime = implode('', $timeArray);
            $dbTime = substr($dbTime, 0, strpos($dbTime, '.') + 9);
            $epochTimes[] = $dbTime;
        }
        $sqlTimes = implode(', ', $epochTimes);
        $data = ['data' => []];
        $times = ['data' => []];
        $sql = "SELECT ac_time, ac_data FROM ac_data WHERE ac_time IN ({$sqlTimes})";
        $result = $DB->query($sql);
        while ($row = $result->fetch()) {
            $rowData = json_decode($row["ac_data"], true);
            for ($i = 0; $i < count($rowData['t']); $i++) {
                if (strpos($rowData['t'][$i], '.') === false) {
                    $rowData['t'][$i] .= '.0';
                }
                $dt = DateTime::createFromFormat('U.u', $rowData['t'][$i]);
                if (!$dt instanceof DateTime) {
                    ob_start();
                    var_dump($rowData['t'][$i], $dt);
                    error_log(ob_get_clean());
                }
                $dt->setTimezone(new DateTimeZone('America/Denver'));
                $data['data'][] = [
                    'name' => $dt->format('H:i:s.v'),
                    'value' => $rowData['d'][$i]
                ];
                $times['data'][] = $dt->format('H:i:s.v');
            }
        }

        $sql = "SELECT case_id FROM peak_test_cases";
        $result = $DB->query($sql);
        while ($row = $result->fetch()) {
            $data['testcase' . $row['case_id']] = [];
        }
        foreach ($epochTimes as $epochTime) {
            $sql = "SELECT * FROM ac_interval_tests WHERE {$epochTime} BETWEEN test_ac_time AND test_end_time";
            $result = $DB->query($sql);
            while ($row = $result->fetch()) {
                $dataset = 'testcase' . $row['test_case_id'];
                $peaks = json_decode($row['test_peak_times']);
                foreach ($peaks as $peakTime) {
                    $dt = DateTime::createFromFormat('U.u', $peakTime);
                    $dt->setTimezone(new DateTimeZone('America/Denver'));
                    $data[$dataset][] = [
                        'name' => $dt->format('H:i:s.v'),
                        'value' => 0.25
                    ];
                    $times[$dataset][] = $dt->format('H:i:s.v');
                }
            }
        }

        foreach ($times as $dataset => $dsTimes) {
            if ($dataset == 'data') continue;
            foreach ($times['data'] as $referenceTime) {
                if (!in_array($referenceTime, $dsTimes)) {
                    $data[$dataset][] = [
                        'name' => $referenceTime,
                        'value' => 0
                    ];
                }
            }
        }


        $formattedData = [];
        foreach ($data as $series => $seriesData) {
            $formattedData[] = [
                'name' => $series,
                'series' => $seriesData
            ];
        }

        echo json_encode($formattedData);
        break;
}
