function connectedDeviceCheck(connectedDeviceInformation){

  function createConnectedDeviceInformation(data){
    const targetDiv = document.getElementById(data.consoleModel);
    const connectedDeviceContainer = document.createElement('div');
    connectedDeviceContainer.classList.add('connected-device-information-container');
    const connectedDeviceDisplay = document.createElement('div');
    connectedDeviceDisplay.classList.add('connected-device-information');
    const connectedDeviceText = document.createTextNode(data.consoleID + ':' + data.consoleIPv4);
    connectedDeviceDisplay.appendChild(connectedDeviceText);
    connectedDeviceContainer.appendChild(connectedDeviceDisplay);
    targetDiv.appendChild(connectedDeviceContainer);
    targetDiv.querySelector('img').classList.add('active');
    setTimeout(function(){
      connectedDeviceContainer.classList.add('active');
    }, 50);
  }

  function removeConnectedDeviceInformation(){
    const connectedDeviceContainer = document.querySelector('.connected-device-information-container');
    connectedDeviceContainer.classList.remove('active');
    connectedDeviceContainer.closest('.product-icon-tile').querySelector('img').classList.remove('active');
    setTimeout(function(){
      connectedDeviceContainer.remove();
    }, 250);
  }

  setInterval(function(){
	fetch('connected-device-check.ajax.php')
    .then(response => response.json())
    .then(data => {
      //console.log(data)
      if ((data.consoleIPv4) && (data.consoleIPv4 != '')){
        if (!document.querySelector('.connected-device-information-container')){
          createConnectedDeviceInformation(data);
        }
        else if (document.querySelector('.connected-device-information-container')){
          let previousConnectedDeviceInformation = document.querySelector('.connected-device-information').innerText;
          let currentConnectedDeviceInformation = data.consoleID + ':' + data.consoleIPv4;
          if (previousConnectedDeviceInformation != currentConnectedDeviceInformation){
            removeConnectedDeviceInformation();
            setTimeout(function(){
              document.querySelector('.connected-device-information').innerText = currentConnectedDeviceInformation;
              createConnectedDeviceInformation(data);
            }, 250);
          }
        }
      }
      else if ((!data.consoleIPv4) || (data.consoleIPv4 == '')){
        if (document.querySelector('.connected-device-information-container')){
          removeConnectedDeviceInformation();
        }
      }
    });
  }, 2000);

}
