-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Aug 25, 2015 at 01:59 PM
-- Server version: 5.5.44-0ubuntu0.14.04.1
-- PHP Version: 5.5.9-1ubuntu4.11

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `aircraft`
--

-- --------------------------------------------------------

--
-- Table structure for table `ids`
--

CREATE TABLE IF NOT EXISTS `ids` (
  `icao` varchar(6) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `regid` varchar(10) DEFAULT NULL,
  `mdl` varchar(5) DEFAULT NULL,
  `fr24` varchar(8) DEFAULT NULL,
  `cs` varchar(10) DEFAULT NULL,
  `fn` varchar(10) DEFAULT NULL,
  `type` varchar(30) DEFAULT NULL,
  `owner` varchar(30) DEFAULT NULL,
  `ts` int(11) DEFAULT NULL,
  PRIMARY KEY (`icao`),
  UNIQUE KEY `icao` (`icao`),
  KEY `regid` (`regid`),
  KEY `fr24` (`fr24`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
