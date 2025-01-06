<?php

require_once('globals.inc.php');
$connection = new Connection();


if ($_GET['action'] == 'gpio-clear-assignment'){
  $connection->resetGPIOInput($_GET['gpio-input-channel']);
}

if ($_GET['action'] == 'insert-gpio-assignment'){
  $connection->updateGPIOInput(
    $_GET['gpio-input-channel'],
    $_GET['active-status'],
    $_GET['latch-status'],
    $_GET['normal-status'],
    $_GET['gpio-mode'],
    $_GET['target-channel']
  );
}

?>
