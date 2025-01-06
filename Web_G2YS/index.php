<?php

require_once('globals.inc.php');

//GETS CURRENTLY ASSIGNED PARAMETERS FOR CONNECTED DEVICE
$connection = new Connection();
$currentControllerAssignments = $connection->getCurrentGPIOInputAssignments();

function checkCurrentActiveStatus($index, $field, $value){
  global $currentControllerAssignments;
  $key = array_search($index, array_column($currentControllerAssignments, 'gpioInputChannel'));
  if ($key > -1){
    if ($currentControllerAssignments[$key][$field] == $value){
      return " active";
    }
  }
}

?>

<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="system.css?v=<?= mt_rand(); ?>">
    <script src="ui.js?v=<?= mt_rand(); ?>"></script>
    <script src="active-sensing.js?v=<?= mt_rand(); ?>"></script>
    <title>GPIO Extender</title>
  </head>
<body>

<h1>Connected Devices</h1>
<div id="CL1" class="product-icon-tile">
  <img src="images/cl1.png" />
</div>
<div id="CL3" class="product-icon-tile">
  <img src="images/cl3.png" />
</div>
<div id="CL5" class="product-icon-tile">
  <img src="images/cl5.png" />
</div>
<div id="QL1" class="product-icon-tile">
  <img src="images/QL1.png" />
</div>
<div id="QL5" class="product-icon-tile">
  <img src="images/QL5.png" />
</div>

<h1>GPIO Input Channels</h1>

<button class="gpio-bank-selector active" data-target="bank-select-0">1-8</button><!--
--><button class="gpio-bank-selector" data-target="bank-select-1">9-16</button><!--
--><button class="gpio-bank-selector" data-target="bank-select-2">17-24</button><!--
--><button class="gpio-bank-selector" data-target="bank-select-3">25-32</button><!--
--><button class="gpio-bank-selector" data-target="bank-select-4">33-40</button><!--
--><button class="gpio-bank-selector" data-target="bank-select-5">41-48</button>
<br /><br />

<?php for ($j = 0; $j <=5; $j++){ ?>
<div class="bank-panel bank-select-<?= $j; ?><?php if ($j == 0) echo ' visible'; ?>">
  <?php for ($i = 1; $i <= 8; $i++){
    $currentGPIOChannel = $i + ($j * 8);
    ?>
    <div class="gpio-channel-row" data-gpio-channel="<?= $currentGPIOChannel; ?>">
      <button class="gpio-program gpio-channel-active">
        <div class="row-1<?= checkCurrentActiveStatus($currentGPIOChannel, 'activeStatus', 1); ?>">#<?= $currentGPIOChannel; ?></div>
        <div class="row-2<?= checkCurrentActiveStatus($currentGPIOChannel, 'activeStatus', 1); ?>">Active</div>
      </button>
      <button class="gpio-program gpio-latch-status">
        <div class="row-1<?= checkCurrentActiveStatus($currentGPIOChannel, 'latchStatus', 'Latch'); ?>">Latch</div>
        <div class="row-2<?= checkCurrentActiveStatus($currentGPIOChannel, 'latchStatus', 'Unlatch'); ?>">Unlatch</div>
      </button>
      <button class="gpio-program gpio-normal-status">
        <div class="row-1<?= checkCurrentActiveStatus($currentGPIOChannel, 'normalStatus', 'N/O'); ?>">N/O</div>
        <div class="row-2<?= checkCurrentActiveStatus($currentGPIOChannel, 'normalStatus', 'N/C'); ?>">N/C</div>
      </button>
      <button class="gpio-program gpio-mode">
        <div class="row-1">Audio Follows Picture</div>
        <div class="row-2">Mute</div>
      </button>
      <button class="gpio-program select-target-channel fixed-width">
        <div class="row-1">Input Channel</div>
        <div class="row-2">No Assign</div>
      </button>
      <button class="clear-gpio-assignment">
        <svg><?= file_get_contents('images/close.svg'); ?></svg>
      </button>
    </div>
  <?php } ?>
</div>
<?php } ?>

<div id="page-overlay-background"></div>
<div id="page-overlay-container">
  <div id="page-overlay-content">
    <h1>Target Input Channel Select</h1>
    <?php for ($j = 0; $j <= 9; $j++){ ?>
      <?php for ($i = 1; $i <= 8; $i++){ ?>
      <button class="gpio-program input-channel-select" data-channel-index="<?= ($i + ($j * 8)); ?>"><?= ($i + ($j * 8)); ?></button>
      <?php } ?>
      <br />
    <?php } ?>
  <div style="text-align: right; margin-top: 20px;"><button class="gpio-program close-page-overlay">Cancel</button></div>
  </div>
</div>

<script>
  connectedDeviceCheck();
  initUI();
</script>

</body>
</html>
