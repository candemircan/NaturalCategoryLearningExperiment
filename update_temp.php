<?php
set_time_limit(3000);
$new_par =  $_POST["nextPar"];
file_put_contents("temp.txt", $new_par);
?>
