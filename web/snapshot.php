<?php
require('config.php');

if($_REQUEST['start']) {
    $DB->query("INSERT INTO snapshots");
}