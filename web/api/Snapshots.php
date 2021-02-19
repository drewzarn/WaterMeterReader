<?php
require('config.php');

switch ($_REQUEST['a']) {
    case 'start':
        $DB->prepare("INSERT INTO snapshots (snap_start_time, snap_name) VALUES(UNIX_TIMESTAMP(), :name)")
            ->execute(['name' => $_REQUEST['name']]);
        echo json_encode(GetSnapshotList());
    break;
    case 'stop':
        $DB->prepare("UPDATE snapshots SET snap_end_time=UNIX_TIMESTAMP() WHERE snap_start_time=:start")
            ->execute(['start' => $_REQUEST['start']]);
        echo json_encode(GetSnapshotList());
    break;
    case 'list':
        echo json_encode(GetSnapshotList());
        break;
}

function GetSnapshotList()
{
    global $DB;
    $result = $DB->query("SELECT snap_start_time, snap_name FROM snapshots WHERE snap_end_time IS NULL");
    $snaps = [];
    while ($row = $result->fetch()) {
        $snaps[] = $row;
    }
    return $snaps;
}
