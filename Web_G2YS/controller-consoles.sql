-- phpMyAdmin SQL Dump
-- version 4.9.5deb2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jul 14, 2020 at 06:07 PM
-- Server version: 8.0.20-0ubuntu0.20.04.1
-- PHP Version: 7.4.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `console_controller`
--

-- --------------------------------------------------------

--
-- Table structure for table `controller_consoles`
--

CREATE TABLE `controller-consoles` (
  `consoleModel` text NOT NULL,
  `consoleID` text NOT NULL,
  `consoleIPv4` text NOT NULL,
  `consoleIsOnline` text NOT NULL,
  `consoleIsSelected` text NOT NULL,
  `consoleIsVirtual` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `controller-consoles` (`consoleModel`, `consoleID`, `consoleIPv4`, `consoleIsOnline`, `consoleIsSelected`, `consoleIsVirtual`) VALUES
('CL3', 'Y003', '192.168.1.123', 'False', 'False', 'True');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
