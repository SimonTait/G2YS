function initUI(){
  const gpioBankSelectButtons = document.querySelectorAll('button.gpio-bank-selector');
  const gpioBankSelectButtonsLength = gpioBankSelectButtons.length;
  for (let i = 0; i < gpioBankSelectButtonsLength; i++){
    gpioBankSelectButtons[i].addEventListener('click', gpioBankSelect);
  }
  const gpioChannelActiveButtons = document.querySelectorAll('button.gpio-channel-active');
  const gpioChannelActiveButtonsLength = gpioChannelActiveButtons.length;
  for (let i = 0; i < gpioChannelActiveButtonsLength; i++){
    gpioChannelActiveButtons[i].addEventListener('click', gpioChannelActive);
  }
  const gpioLatchStatusButtons = document.querySelectorAll('button.gpio-latch-status');
  const gpioLatchStatusButtonsLength = gpioLatchStatusButtons.length;
  for (let i = 0; i < gpioLatchStatusButtonsLength; i++){
    gpioLatchStatusButtons[i].addEventListener('click', gpioLatchStatus);
  }
  const gpioNormalStatusButtons = document.querySelectorAll('button.gpio-normal-status');
  const gpioNormalStatusButtonsLength = gpioNormalStatusButtons.length;
  for (let i = 0; i < gpioNormalStatusButtonsLength; i++){
    gpioNormalStatusButtons[i].addEventListener('click', gpioNormalStatus);
  }
  const gpioModeButtons = document.querySelectorAll('button.gpio-mode');
  const gpioModeButtonsLength = gpioModeButtons.length;
  for (let i = 0; i < gpioModeButtonsLength; i++){
    gpioModeButtons[i].addEventListener('click', gpioMode);
  }
  const gpioTargetChannelButtons = document.querySelectorAll('button.select-target-channel');
  const gpioTargetChannelButtonsLength = gpioTargetChannelButtons.length;
  for (let i = 0; i < gpioTargetChannelButtonsLength; i++){
    gpioTargetChannelButtons[i].addEventListener('click', gpioTargetChannel);
  }
  const gpioTargetChannelSelectButtons = document.querySelectorAll('button.input-channel-select');
  const gpioTargetChannelSelectButtonsLength = gpioTargetChannelSelectButtons.length;
  for (let i = 0; i < gpioTargetChannelSelectButtonsLength; i++){
    gpioTargetChannelSelectButtons[i].addEventListener('click', gpioTargetChannelSelect);
  }
  const gpioClearAssignmentButtons = document.querySelectorAll('button.clear-gpio-assignment');
  const gpioClearAssignmentButtonsLength = gpioClearAssignmentButtons.length;
  for (let i = 0; i < gpioClearAssignmentButtonsLength; i++){
    gpioClearAssignmentButtons[i].addEventListener('click', gpioClearAssignment);
  }
  document.querySelector('button.close-page-overlay').addEventListener('click', closePageOverlay);
}

function gpioBankSelect(){
  document.querySelector('button.gpio-bank-selector.active').classList.remove('active');
  this.classList.add('active');
  document.querySelector('.bank-panel.visible').classList.remove('visible');
  document.querySelector('.bank-panel.' + this.dataset.target).classList.add('visible');
}

function gpioChannelActive(){
  this.querySelector('.row-1').classList.toggle('active');
  this.querySelector('.row-2').classList.toggle('active');
  gpioUpdateAssignment(this.closest('div'));
}

function gpioLatchStatus(){
  if (!this.querySelector('.active')){
    this.querySelector('.row-1').classList.toggle('active');
  } else{
    this.querySelector('.row-1').classList.toggle('active');
    this.querySelector('.row-2').classList.toggle('active');
  }
  gpioUpdateAssignment(this.closest('div'));
}

function gpioNormalStatus(){
  if (!this.querySelector('.active')){
    this.querySelector('.row-1').classList.toggle('active');
  } else{
    this.querySelector('.row-1').classList.toggle('active');
    this.querySelector('.row-2').classList.toggle('active');
  }
  gpioUpdateAssignment(this.closest('div'));
}

function gpioMode(){
  if (!this.querySelector('.active')){
    this.querySelector('.row-1').classList.toggle('active');
  } else{
    this.querySelector('.row-1').classList.toggle('active');
    this.querySelector('.row-2').classList.toggle('active');
  }
  gpioUpdateAssignment(this.closest('div'));
}

function gpioTargetChannel(){
  document.getElementById('page-overlay-background').classList.add('visible');
  document.getElementById('page-overlay-container').classList.add('visible');
  document.getElementById('page-overlay-content').dataset.gpioChannel = this.closest('div').dataset.gpioChannel;
  if (document.getElementById('page-overlay-content').querySelector('[data-channel-index="' + this.querySelector('.row-2').innerText + '"]')){
    document.getElementById('page-overlay-content').querySelector('[data-channel-index="' + this.querySelector('.row-2').innerText + '"]').classList.add('active');
  }
}

function gpioTargetChannelSelect(){
  const targetRowIndex = this.closest('div').dataset.gpioChannel;
  const targetRow = document.querySelector('div[data-gpio-channel="' + targetRowIndex + '"]');
  targetRow.querySelector('.select-target-channel').querySelector('.row-1').classList.add('active');
  targetRow.querySelector('.select-target-channel').querySelector('.row-2').classList.add('active');
  targetRow.querySelector('.select-target-channel').querySelector('.row-2').innerText = this.innerText;
  closePageOverlay();
  gpioUpdateAssignment(targetRow);
}

function closePageOverlay(){
  if (document.getElementById('page-overlay-content').querySelector('.active')){
    document.getElementById('page-overlay-content').querySelector('.active').classList.remove('active');
  }
  document.getElementById('page-overlay-background').classList.remove('visible');
  document.getElementById('page-overlay-container').classList.remove('visible');
}

function gpioClearAssignment(){
  const gpioChannel = this.closest('div').dataset.gpioChannel;
  const gpioChannelRow = this.closest('div');
  const activeText = gpioChannelRow.querySelectorAll('.active');
  const activeTextLength = activeText.length;
  for (let i = 0; i < activeTextLength; i++){
    activeText[i].classList.remove('active');
  }
  const fetchURL = 'db-io.ajax.php?action=gpio-clear-assignment&gpio-input-channel=' + gpioChannel;
  fetch(fetchURL);
  setTimeout(function(){
    gpioChannelRow.querySelector('.select-target-channel').querySelector('.row-2').innerText = "No Assign";
  }, 250);
}

function gpioUpdateAssignment(source){
  let gpioInputChannel = source.dataset.gpioChannel;
  let activeStatus = source.querySelector('button.gpio-channel-active').querySelector('.active');
  if (!activeStatus){
    activeStatus = '';
  } else {
    activeStatus = 1;
  }
  let latchStatus = source.querySelector('button.gpio-latch-status').querySelector('.active');
  if (!latchStatus){
    latchStatus = '';
  } else {
    latchStatus = latchStatus.innerText;
  }
  let normalStatus = source.querySelector('button.gpio-normal-status').querySelector('.active');
  if (!normalStatus){
    normalStatus = '';
  } else {
    normalStatus = normalStatus.innerText;
  }
  let gpioMode = source.querySelector('button.gpio-mode').querySelector('.active');
  if (!gpioMode){
    gpioMode = '';
  } else {
    gpioMode = gpioMode.innerText;
  }
  let targetChannel = source.querySelector('button.select-target-channel').querySelector('.row-2').innerText;
  if (targetChannel == 'No Assign'){
    targetChannel = '';
  } else {
    targetChannel = targetChannel;
  }
  let fetchURL = 'db-io.ajax.php?action=insert-gpio-assignment&gpio-input-channel=' + gpioInputChannel;
  fetchURL += '&active-status=' + activeStatus;
  fetchURL += '&latch-status=' + latchStatus;
  fetchURL += '&normal-status=' + normalStatus;
  fetchURL += '&gpio-mode=' + gpioMode;
  fetchURL += '&target-channel=' + targetChannel;
  fetch(fetchURL);
}
