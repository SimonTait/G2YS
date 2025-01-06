<?php

//JSON FILE READ FOR CONNECTED DEVICE GLOBALS
//$json = file_get_contents("connected-device.json");

// GRAB THE CONNECTED DEVICE FROM THE `controller-consoles` TABLE
require_once('globals.inc.php');
$connection = new Connection();
$console = $connection->getConnectedConsole();

if (!$console) {
    $noConsole = file_get_contents("dummy-device.json");
    $json = json_encode($noConsole);
    $connectedDevice = json_decode($json);
}

else {
    $json = json_encode($console[0]);
    $connectedDevice = json_decode($json);
   
    switch ($connectedDevice->consoleModel){
      case "CL1":
        $connectedDevice->inputChannelCount = 48;
        break;
      case "CL3":
        $connectedDevice->inputChannelCount = 64;
        break;
      case "CL5":
        $connectedDevice->inputChannelCount = 72;
        break;
    }
}

$connectedDevice = json_encode($connectedDevice);
    
print_r($connectedDevice);

?>
