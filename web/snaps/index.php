<?php

$files = array();
if ($handle = opendir('../../imageprocessing')) {
    while (false !== ($file = readdir($handle))) {
        if ($file != "." && $file != ".." && substr($file, -4) == '.png') {
           $files[filemtime($file)] = $file;
        }
    }
    closedir($handle);

    // sort
    ksort($files);
	$files = array_reverse($files);
	if(isset($_REQUEST['latest'])) {
		$lastFile = $files[array_keys($files)[0]];
		if(filesize($lastFile) == 0) {
			$lastFile = $files[array_keys($files)[1]];
		}
		echo '<meta http-equiv="refresh" content="2"; />';
		echo "<h1>{$lastFile}</h1><br />";
		echo "<img style=\"height: 100%\" src=\"{$lastFile}\" />";
	} else {
		foreach($files as $file) {
			echo "<a href=\"$file\">$file</a><br />";
		}
	}
}

