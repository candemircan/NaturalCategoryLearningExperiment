<?php
// get the data from the POST message
$post_data = json_decode(file_get_contents('php://input'), true);
$data = $post_data['filedata'];
$data_type = $post_data['datatype'];
$file = $post_data['subjectid'];
// the directory "data" must be writable by the server
$name = "data/{$data_type}_{$file}.csv"; 
// write the file to disk
file_put_contents($name, $data);
?>
