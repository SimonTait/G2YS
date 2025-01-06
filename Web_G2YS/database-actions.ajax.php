<?php

require_once('globals.inc.php');
$connection = new Connection();

if ($_GET['action'] == 'update-gpio-input'){
  $connection->updateGPIOInput($_POST['gpio-input-channel'], $_POST['active-status'], $_POST['latch-status'], $_POST['normal-status'], $_POST['function-name']);
}

if ($_GET['action'] == 'reset-gpio-input'){
  $connection->resetGPIOInput($_GET['gpio-input-channel']);
}
