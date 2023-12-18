-- MariaDB dump 10.19  Distrib 10.11.4-MariaDB, for debian-linux-gnu (aarch64)
--
-- Host: localhost    Database: openSolar
-- ------------------------------------------------------
-- Server version	10.11.4-MariaDB-1~deb12u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log` (
  `sensorId` tinytext NOT NULL,
  `time` bigint(20) unsigned DEFAULT NULL,
  `value` decimal(5,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `status`
--

DROP TABLE IF EXISTS `status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `status` (
  `sensorId` varchar(25) NOT NULL,
  `value` float DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  `time` bigint(20) unsigned DEFAULT unix_timestamp(),
  UNIQUE KEY `status_sensorId_IDX` (`sensorId`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `status`
--

LOCK TABLES `status` WRITE;
/*!40000 ALTER TABLE `status` DISABLE KEYS */;
INSERT INTO `status` VALUES
('control0-loop-onoff',1,'0: off 1: on Control system on and off.',1702688662),
('control1-off2onThress',60,'The temperature in C at which the pump will tuen on. This must be higher than on2off.',1702807631),
('control1-on2offThress',4,'The temperature in C at which the pump will turn from on to off.',1702681383),
('cvcc',0,'R: Constant voltage or Constant current.',1702679078),
('fw-version',1.4,'R: Firmware version of dsp5005',1702679078),
('i-out',0,'R: The current being drawn in Amps.',1702679078),
('i-set',0.7,'R/W: The maximum current in Amps.',1702679078),
('lock',0,'R/W: Lock the dsp5005 interface.',1702679078),
('model',5005,'R: The model number.',1702679078),
('on',0,'R/W: 0: off 1: on if the dsp5005 sending voltage. ',1702679078),
('power',0,'R: The calculated watts being sent to the pump ',1702679078),
('protect',0,'R: One of the three safty conditions; s-ocp,s-opp,s,ovp has been reached. ',1702679078),
('s-ocp',0.8,'R/W: The Over current protection set point in Amps',1702679078),
('s-opp',2652,'R/W: The Over power protection set point in watts.',1702679078),
('s-ovp',12.5,'R/W: The Over voltage protection set point in volts.',1702679078),
('t1',14.66,'R: Tank top temperature in C',1702679078),
('t2',14.05,'R: Tank bottom temperature in C',1702679078),
('t3',7.46,'R: Collector in temperature in C',1702679078),
('t4',7.15,'R: Collector out temperature in C',1702679078),
('u-in',15.37,'R: Voltage supply in.',1702679078),
('u-out',0,'R: Voltage out reading.',1702679078),
('u-set',12,'R/W: Set voltage out.',1702679078);
/*!40000 ALTER TABLE `status` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-17 23:41:59
