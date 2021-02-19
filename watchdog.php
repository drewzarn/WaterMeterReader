<?php
error_reporting(E_ERROR);
gc_enable();
require('web/api/config.php');

while (PHP_SAPI == "cli") {
    $result = $DB->query("SELECT * FROM processes WHERE proc_run=1");

    while ($row = $result->fetch()) {
        $procParts = explode('/', $row['proc_path']);
        $procName = $procParts[count($procParts) - 1];

        $procResult = exec("ps aux | grep {$procName} | grep -v grep");

        if ($procResult != "") {
            syslog(LOG_INFO, "Process found for {$row['proc_name']}");
        } else {
            syslog(LOG_INFO, "Launching {$row['proc_name']}");
            exec("{$row['proc_path']} > {$row['proc_path']}.output &");
            $procResult = exec("ps aux | grep {$procName} | grep -v grep");
        }
    }
    sleep(10);
}
