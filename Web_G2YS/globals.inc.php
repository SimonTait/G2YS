<?php
//MYSQL DATABASE CONNECTION AND QUERIES
class Connection{

  protected function connectDB(){

    $this->hostname = 'localhost';
    $this->username = 'root';
    $this->password = 'allenallen';
    //$this->password = 'root';
    $this->database = 'console_controller';
    $this->charset = 'utf8mb4';

    $dsn = 'mysql:host='.$this->hostname.';dbname='.$this->database.';charset='.$this->charset;;
    $pdoOptions = [
      PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
      PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ];
    $pdo = new PDO($dsn, $this->username, $this->password, $pdoOptions);
    return $pdo;
  }

  protected function queryDB($query, $queryParameters=null){
    $stmt = $this->connectDB()->prepare($query);
    if ($queryParameters){
      foreach ($queryParameters as $bindKey => &$bindValue){
        $stmt->bindParam($bindKey, $bindValue);
      }
    }
    $stmt->execute();
    $result = $stmt->fetchAll();
    if ($result){
      return $result;
    }
  }

  public function getConnectedConsole () {
      $query = "SELECT * from `controller-consoles` WHERE `consoleIsOnline`='True'";
      $result = $this->queryDB($query);
      if ($result){
          return $result;
      }
  }

  public function writeDB($query, $queryParameters=null){
    $stmt = $this->connectDB()->prepare($query);
    if ($queryParameters){
      foreach ($queryParameters as $bindKey => &$bindValue){
        $stmt->bindParam($bindKey, $bindValue);
      }
    }
    $stmt->execute();
  }

  public function getCurrentGPIOInputAssignments(){
    $query = "SELECT gpioInputChannel, activeStatus, latchStatus, normalStatus, functionName
    FROM controller_assignments
    ORDER BY gpioInputChannel";
    $result = $this->queryDB($query);
    if ($result){
      return $result;
    }
  }

  public function resetGPIOInput($gpioInputChannel){
    $delete = "DELETE FROM controller_assignments WHERE gpioInputChannel = $gpioInputChannel";
    $this->writeDB($delete);
  }

  public function updateGPIOInput(
      $gpioInputChannel,
      $activeStatus,
      $latchStatus,
      $normalStatus,
      $functionName,
      $targetChannel
    ){
    $this->resetGPIOInput($gpioInputChannel);
    $insert = "INSERT IGNORE INTO controller_assignments
    (gpioInputChannel, activeStatus, latchStatus, normalStatus, functionName, targetChannel)
    VALUES (:gpioInputChannel, :activeStatus, :latchStatus, :normalStatus, :functionName, :targetChannel)";
    $insertParameters = array();
    $insertParameters[':gpioInputChannel'] = $gpioInputChannel;
    $insertParameters[':activeStatus'] = $activeStatus;
    $insertParameters[':latchStatus'] = $latchStatus;
    $insertParameters[':normalStatus'] = $normalStatus;
    $insertParameters[':functionName'] = $functionName;
    $insertParameters[':targetChannel'] = $targetChannel;
    $this->writeDB($insert, $insertParameters);
  }


}

?>
