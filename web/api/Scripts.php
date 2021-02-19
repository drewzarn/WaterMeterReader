<?php
require('config.php');
$dbResult = $DB->query("SELECT * FROM processes ORDER BY proc_name");
$services = [];

$procResult = exec("ps aux | grep watchdog.php | grep -v grep");
$services[] = ['name' => 'Watchdog', 'run' => true, 'running' => $procResult != ""];

while ($row = $dbResult->fetch()) {
    $procParts = explode('/', $row['proc_path']);
    $procName = $procParts[count($procParts) - 1];
    $procResult = exec("ps aux | grep {$procName} | grep -v grep");

    $services[] = ['name' => $row['proc_name'], 'run' => $row['proc_run'] == 1, 'running' => $procResult != ""];
}

echo json_encode($services);
