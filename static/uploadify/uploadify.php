<?php
/*
Uploadify
Copyright (c) 2012 Reactive Apps, Ronnie Garcia
Released under the MIT License <http://www.opensource.org/licenses/mit-license.php>
*/
ini_set('display_errors',1);
ini_set('display_startup_errors',1);
error_reporting(E_ALL);

echo exec('whoami'), "\n";
// Define a destination
$targetFolder = '/upload'; // Relative to the root
#echo $_POST['token'];
$verifyToken = md5('unique_salt' . $_POST['timestamp']);
if (!empty($_FILES) && $_POST['token'] == $verifyToken) {
	$tempFile = $_FILES['Filedata']['tmp_name'];
	$targetPath = $_SERVER['DOCUMENT_ROOT'] . $targetFolder;
	$targetFile = rtrim($targetPath,'/') . '/' . $_FILES['Filedata']['name'];
	// Validate the file type
	$fileTypes = array('mp4','mov','MOV','wmv','avi','webm','ogg','wav'); // File extensions
	$fileParts = pathinfo($_FILES['Filedata']['name']);
	echo $targetFile, "\n";
	if (in_array($fileParts['extension'],$fileTypes)) {
		echo move_uploaded_file($tempFile,$targetFile), "\n";
		echo '1', "\n";
	} else {
		echo 'Invalid file type. \n';
	}
}
echo 'post finished';
?>
