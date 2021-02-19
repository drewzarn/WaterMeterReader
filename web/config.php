<?php
$DBHOST = "localhost";
$DBUSER = "meterdb";
$DBPASS = "meterpass";
$DBNAME = "meters";

$dsn = "mysql:host=$DBHOST;dbname=$DBNAME;";
$DBOptions = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,
];
try {
     $DB = new PDO($dsn, $DBUSER, $DBPASS, $DBOptions);
} catch (\PDOException $e) {
     throw new \PDOException($e->getMessage(), (int)$e->getCode());
}