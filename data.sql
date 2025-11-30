-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: chatdb
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `chat_group`
--

DROP TABLE IF EXISTS `chat_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `created_by` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_group_creator` (`created_by`),
  CONSTRAINT `fk_group_creator` FOREIGN KEY (`created_by`) REFERENCES `userdata` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_group`
--

LOCK TABLES `chat_group` WRITE;
/*!40000 ALTER TABLE `chat_group` DISABLE KEYS */;
INSERT INTO `chat_group` VALUES (27,'beta',6,'2025-11-11 11:48:57'),(28,'mahendra',6,'2025-11-11 11:51:20'),(35,'bokka',7,'2025-11-14 10:24:15'),(36,'phabas',5,'2025-11-15 11:20:06'),(37,'team',8,'2025-11-15 13:04:45'),(38,'team 1',5,'2025-11-16 12:19:23');
/*!40000 ALTER TABLE `chat_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group_member`
--

DROP TABLE IF EXISTS `group_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `group_member` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `user_id` int NOT NULL,
  `joined_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_group_user` (`group_id`,`user_id`),
  KEY `idx_member_user` (`user_id`),
  KEY `idx_member_group` (`group_id`),
  CONSTRAINT `group_member_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `chat_group` (`id`) ON DELETE CASCADE,
  CONSTRAINT `group_member_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `userdata` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group_member`
--

LOCK TABLES `group_member` WRITE;
/*!40000 ALTER TABLE `group_member` DISABLE KEYS */;
INSERT INTO `group_member` VALUES (5,27,4,'2025-11-11 11:48:57'),(6,27,5,'2025-11-11 11:48:57'),(7,27,6,'2025-11-11 11:48:57'),(8,28,4,'2025-11-11 11:51:20'),(9,28,5,'2025-11-11 11:51:20'),(10,28,6,'2025-11-11 11:51:20'),(26,35,4,'2025-11-14 10:24:15'),(27,35,5,'2025-11-14 10:24:15'),(28,35,7,'2025-11-14 10:24:15'),(29,36,4,'2025-11-15 11:20:06'),(30,36,5,'2025-11-15 11:20:06'),(31,36,6,'2025-11-15 11:20:06'),(32,36,7,'2025-11-15 11:20:06'),(33,37,8,'2025-11-15 13:04:45'),(36,38,8,'2025-11-16 12:19:23'),(37,38,4,'2025-11-16 12:19:23'),(39,38,7,'2025-11-16 12:19:23');
/*!40000 ALTER TABLE `group_member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message`
--

DROP TABLE IF EXISTS `message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `message` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `sender_id` int NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `file_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sender_id` (`sender_id`),
  KEY `idx_group_time` (`group_id`,`created_at`),
  CONSTRAINT `message_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `chat_group` (`id`) ON DELETE CASCADE,
  CONSTRAINT `message_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `userdata` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message`
--

LOCK TABLES `message` WRITE;
/*!40000 ALTER TABLE `message` DISABLE KEYS */;
INSERT INTO `message` VALUES (30,27,6,'hiii','2025-11-11 11:49:05',NULL),(31,27,5,'hello','2025-11-11 11:49:18',NULL),(32,28,5,'💇','2025-11-11 11:51:51',NULL),(33,28,6,'hai','2025-11-11 11:52:16',NULL),(34,28,4,'ewwwww......','2025-11-11 11:54:55',NULL),(35,28,6,'😎','2025-11-11 12:05:42',NULL),(36,28,5,'a','2025-11-11 12:08:26',NULL),(37,28,6,'b','2025-11-11 12:08:34',NULL),(38,28,4,'c','2025-11-11 12:08:46',NULL),(43,28,5,'hii','2025-11-12 12:25:11',NULL),(44,28,5,'abc','2025-11-12 12:25:33',NULL),(45,28,5,'a','2025-11-12 12:25:35',NULL),(46,28,5,'b','2025-11-12 12:25:36',NULL),(47,28,5,'c','2025-11-12 12:25:38',NULL),(48,28,5,'d','2025-11-12 12:25:39',NULL),(49,28,5,'e','2025-11-12 12:25:41',NULL),(50,28,5,'f','2025-11-12 12:25:41',NULL),(51,28,5,'g','2025-11-12 12:25:42',NULL),(52,28,5,'h','2025-11-12 12:25:43',NULL),(53,28,5,'i','2025-11-12 12:25:44',NULL),(54,28,5,'j','2025-11-12 12:25:45',NULL),(55,28,5,'k','2025-11-12 12:25:50',NULL),(56,28,5,'l','2025-11-12 12:25:50',NULL),(57,28,5,'m','2025-11-12 12:25:52',NULL),(58,28,5,'n','2025-11-12 12:25:52',NULL),(59,28,5,'o','2025-11-12 12:25:53',NULL),(60,28,5,'p','2025-11-12 12:25:54',NULL),(61,28,5,'q','2025-11-12 12:25:56',NULL),(62,28,5,'r','2025-11-12 12:25:57',NULL),(63,28,5,'s','2025-11-12 12:25:58',NULL),(64,28,5,'t','2025-11-12 12:25:59',NULL),(65,28,5,'u','2025-11-12 12:26:00',NULL),(66,28,5,'v','2025-11-12 12:26:02',NULL),(67,28,5,'w','2025-11-12 12:26:05',NULL),(68,28,5,'x','2025-11-12 12:26:07',NULL),(69,28,5,'y','2025-11-12 12:26:08',NULL),(70,28,5,'z','2025-11-12 12:26:09',NULL),(71,28,4,'what happened','2025-11-12 12:46:08',NULL),(74,28,5,'hii','2025-11-13 17:08:58',NULL),(75,28,5,'hello','2025-11-13 17:26:40',NULL),(76,28,4,'💯','2025-11-13 18:22:38',NULL),(77,28,4,'❤️','2025-11-13 18:22:43',NULL),(78,28,4,'Shared file: 61N03oj9kyL._SY879_.jpg','2025-11-13 18:28:38',NULL),(79,28,4,'Shared file: 71VhDFidEeL._SX679_.jpg','2025-11-13 18:32:12',NULL),(80,28,4,'Shared file: 61N03oj9kyL._SY879_.jpg','2025-11-13 18:38:18',NULL),(81,28,4,'Shared file: 61RNY9kOiyL._SX679_.jpg','2025-11-13 18:41:47',NULL),(82,28,4,'Shared file: 713jJTqsocL._SX679_.jpg','2025-11-13 18:44:57','/static\\uploads\\3d5abc698314420bb52050cb7be10f18.jpg'),(83,28,4,'Shared file: 61N03oj9kyL._SY879_.jpg','2025-11-14 05:22:41','/static\\uploads\\67c32d8c29e2412490464af567b1bea8.jpg'),(84,28,4,'Shared file: 61N03oj9kyL._SY879_.jpg','2025-11-14 05:35:08','/static\\uploads\\1f5b3258ee4d4636822731e7a2b6febc.jpg'),(85,28,4,'Shared file: 713jJTqsocL._SX679_.jpg','2025-11-14 05:36:45','/static\\uploads\\1cc1f0150ac7496297e65a3af67837e6.jpg'),(86,28,5,'Shared file: 61N03oj9kyL._SY879_.jpg','2025-11-14 05:40:43','/static\\uploads\\e5bf03e9f44d4b0191a3d58fe595614c.jpg'),(87,28,5,'Shared file: ANIL FINAL RESUME.pdf','2025-11-14 05:49:04','/static\\uploads\\bf21753580f64b5ca6d2e96405aae364.pdf'),(88,35,7,'hello','2025-11-14 10:24:32',NULL),(89,35,7,'👀','2025-11-14 10:24:37',NULL),(90,35,7,'Shared file: 61g9YCGFuFL._SX679_.jpg','2025-11-14 10:24:42','/static\\uploads\\8f3ec7b580d6431992715f0f4642ff3f.jpg'),(91,35,7,'Shared file: ANIL FINAL RESUME.pdf','2025-11-14 10:24:51','/static\\uploads\\97edbb131d474e31b4fc7bd7dce339a5.pdf'),(92,35,4,'hello','2025-11-14 11:29:15',NULL),(93,35,4,'chapu raa','2025-11-14 11:29:21',NULL),(94,35,4,'💯','2025-11-14 11:29:26',NULL),(95,35,5,'hello','2025-11-15 05:31:02',NULL),(96,36,5,'hello','2025-11-15 12:13:31',NULL),(97,37,8,'hello','2025-11-15 13:05:12',NULL),(98,37,4,'💯','2025-11-15 13:07:16',NULL),(99,38,5,'hello','2025-11-16 12:19:33',NULL),(100,38,5,'😂','2025-11-16 12:21:29',NULL),(101,38,5,'Shared file: dasboaed.jpg','2025-11-16 12:21:38','/static\\uploads\\e648a0139d5d418e9cff9964eea9e814.jpg'),(102,38,4,'bagunnara','2025-11-29 05:03:33',NULL);
/*!40000 ALTER TABLE `message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message_read`
--

DROP TABLE IF EXISTS `message_read`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `message_read` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `message_id` bigint NOT NULL,
  `user_id` int NOT NULL,
  `read_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_msg_user` (`message_id`,`user_id`),
  KEY `idx_read_user` (`user_id`),
  CONSTRAINT `message_read_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `message` (`id`) ON DELETE CASCADE,
  CONSTRAINT `message_read_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `userdata` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=245 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message_read`
--

LOCK TABLES `message_read` WRITE;
/*!40000 ALTER TABLE `message_read` DISABLE KEYS */;
INSERT INTO `message_read` VALUES (23,30,4,'2025-11-11 16:23:47'),(24,30,5,'2025-11-11 11:49:14'),(25,30,6,'2025-11-11 11:49:05'),(26,31,4,'2025-11-11 16:23:47'),(27,31,5,'2025-11-11 11:49:18'),(28,31,6,'2025-11-11 11:49:18'),(29,32,4,'2025-11-11 11:54:45'),(30,32,5,'2025-11-11 11:51:51'),(31,32,6,'2025-11-11 11:52:04'),(32,33,4,'2025-11-11 11:54:45'),(33,33,5,'2025-11-11 11:52:16'),(34,33,6,'2025-11-11 11:52:16'),(35,34,4,'2025-11-11 11:54:55'),(36,34,5,'2025-11-11 11:54:55'),(37,34,6,'2025-11-11 11:54:55'),(38,35,4,'2025-11-11 12:06:30'),(39,35,5,'2025-11-11 12:07:34'),(40,35,6,'2025-11-11 12:05:42'),(41,36,4,'2025-11-11 12:08:42'),(42,36,5,'2025-11-11 12:08:26'),(43,36,6,'2025-11-11 12:08:26'),(44,37,4,'2025-11-11 12:08:42'),(45,37,5,'2025-11-11 12:08:34'),(46,37,6,'2025-11-11 12:08:34'),(47,38,4,'2025-11-11 12:08:46'),(48,38,5,'2025-11-11 12:08:46'),(49,38,6,'2025-11-11 12:08:46'),(62,43,4,'2025-11-12 12:45:51'),(63,43,5,'2025-11-12 12:25:11'),(64,43,6,NULL),(65,44,4,'2025-11-12 12:45:51'),(66,44,5,'2025-11-12 12:25:33'),(67,44,6,NULL),(68,45,4,'2025-11-12 12:45:51'),(69,45,5,'2025-11-12 12:25:35'),(70,45,6,NULL),(71,46,4,'2025-11-12 12:45:51'),(72,46,5,'2025-11-12 12:25:36'),(73,46,6,NULL),(74,47,4,'2025-11-12 12:45:51'),(75,47,5,'2025-11-12 12:25:38'),(76,47,6,NULL),(77,48,4,'2025-11-12 12:45:51'),(78,48,5,'2025-11-12 12:25:39'),(79,48,6,NULL),(80,49,4,'2025-11-12 12:45:51'),(81,49,5,'2025-11-12 12:25:41'),(82,49,6,NULL),(83,50,4,'2025-11-12 12:45:51'),(84,50,5,'2025-11-12 12:25:41'),(85,50,6,NULL),(86,51,4,'2025-11-12 12:45:51'),(87,51,5,'2025-11-12 12:25:42'),(88,51,6,NULL),(89,52,4,'2025-11-12 12:45:51'),(90,52,5,'2025-11-12 12:25:43'),(91,52,6,NULL),(92,53,4,'2025-11-12 12:45:51'),(93,53,5,'2025-11-12 12:25:44'),(94,53,6,NULL),(95,54,4,'2025-11-12 12:45:51'),(96,54,5,'2025-11-12 12:25:45'),(97,54,6,NULL),(98,55,4,'2025-11-12 12:45:51'),(99,55,5,'2025-11-12 12:25:50'),(100,55,6,NULL),(101,56,4,'2025-11-12 12:45:51'),(102,56,5,'2025-11-12 12:25:50'),(103,56,6,NULL),(104,57,4,'2025-11-12 12:45:51'),(105,57,5,'2025-11-12 12:25:52'),(106,57,6,NULL),(107,58,4,'2025-11-12 12:45:51'),(108,58,5,'2025-11-12 12:25:52'),(109,58,6,NULL),(110,59,4,'2025-11-12 12:45:51'),(111,59,5,'2025-11-12 12:25:53'),(112,59,6,NULL),(113,60,4,'2025-11-12 12:45:51'),(114,60,5,'2025-11-12 12:25:54'),(115,60,6,NULL),(116,61,4,'2025-11-12 12:45:51'),(117,61,5,'2025-11-12 12:25:56'),(118,61,6,NULL),(119,62,4,'2025-11-12 12:45:51'),(120,62,5,'2025-11-12 12:25:57'),(121,62,6,NULL),(122,63,4,'2025-11-12 12:45:51'),(123,63,5,'2025-11-12 12:25:58'),(124,63,6,NULL),(125,64,4,'2025-11-12 12:45:51'),(126,64,5,'2025-11-12 12:25:59'),(127,64,6,NULL),(128,65,4,'2025-11-12 12:45:51'),(129,65,5,'2025-11-12 12:26:00'),(130,65,6,NULL),(131,66,4,'2025-11-12 12:45:51'),(132,66,5,'2025-11-12 12:26:02'),(133,66,6,NULL),(134,67,4,'2025-11-12 12:45:51'),(135,67,5,'2025-11-12 12:26:05'),(136,67,6,NULL),(137,68,4,'2025-11-12 12:45:51'),(138,68,5,'2025-11-12 12:26:07'),(139,68,6,NULL),(140,69,4,'2025-11-12 12:45:51'),(141,69,5,'2025-11-12 12:26:08'),(142,69,6,NULL),(143,70,4,'2025-11-12 12:45:51'),(144,70,5,'2025-11-12 12:26:09'),(145,70,6,NULL),(146,71,4,'2025-11-12 12:46:08'),(147,71,5,'2025-11-13 10:45:15'),(148,71,6,NULL),(153,74,4,'2025-11-13 18:19:14'),(154,74,5,'2025-11-13 17:08:58'),(155,74,6,NULL),(156,75,4,'2025-11-13 18:19:14'),(157,75,5,'2025-11-13 17:26:40'),(158,75,6,NULL),(159,76,4,'2025-11-13 18:22:38'),(160,76,5,'2025-11-14 05:37:09'),(161,76,6,NULL),(162,77,4,'2025-11-13 18:22:43'),(163,77,5,'2025-11-14 05:37:09'),(164,77,6,NULL),(165,78,4,'2025-11-13 18:28:38'),(166,78,5,'2025-11-14 05:37:09'),(167,78,6,NULL),(168,79,4,'2025-11-13 18:32:12'),(169,79,5,'2025-11-14 05:37:09'),(170,79,6,NULL),(171,80,4,'2025-11-13 18:38:18'),(172,80,5,'2025-11-14 05:37:09'),(173,80,6,NULL),(174,81,4,'2025-11-13 18:41:47'),(175,81,5,'2025-11-14 05:37:09'),(176,81,6,NULL),(177,82,4,'2025-11-13 18:44:57'),(178,82,5,'2025-11-14 05:37:09'),(179,82,6,NULL),(180,83,4,'2025-11-14 05:22:41'),(181,83,5,'2025-11-14 05:37:09'),(182,83,6,NULL),(183,84,4,'2025-11-14 05:35:08'),(184,84,5,'2025-11-14 05:37:09'),(185,84,6,NULL),(186,85,4,'2025-11-14 05:36:45'),(187,85,5,'2025-11-14 05:37:09'),(188,85,6,NULL),(189,86,4,NULL),(190,86,5,'2025-11-14 05:40:43'),(191,86,6,NULL),(192,87,4,NULL),(193,87,5,'2025-11-14 05:49:04'),(194,87,6,NULL),(195,88,4,'2025-11-14 11:29:07'),(196,88,5,'2025-11-14 11:29:32'),(197,88,7,'2025-11-14 10:24:32'),(198,89,4,'2025-11-14 11:29:07'),(199,89,5,'2025-11-14 11:29:32'),(200,89,7,'2025-11-14 10:24:37'),(201,90,4,'2025-11-14 11:29:07'),(202,90,5,'2025-11-14 11:29:32'),(203,90,7,'2025-11-14 10:24:42'),(204,91,4,'2025-11-14 11:29:07'),(205,91,5,'2025-11-14 11:29:32'),(206,91,7,'2025-11-14 10:24:51'),(207,92,4,'2025-11-14 11:29:16'),(208,92,5,'2025-11-14 11:29:32'),(209,92,7,NULL),(210,93,4,'2025-11-14 11:29:21'),(211,93,5,'2025-11-14 11:29:32'),(212,93,7,NULL),(213,94,4,'2025-11-14 11:29:26'),(214,94,5,'2025-11-14 11:29:32'),(215,94,7,NULL),(216,95,4,NULL),(217,95,5,'2025-11-15 05:31:02'),(218,95,7,NULL),(219,96,4,NULL),(220,96,5,'2025-11-15 12:13:31'),(221,96,6,NULL),(222,96,7,NULL),(223,97,4,'2025-11-15 13:07:10'),(224,97,5,'2025-11-18 11:04:17'),(225,97,8,'2025-11-15 13:05:12'),(226,98,4,'2025-11-15 13:07:16'),(227,98,5,'2025-11-18 11:04:17'),(228,98,8,'2025-11-15 13:07:21'),(229,99,4,'2025-11-16 12:20:09'),(230,99,5,'2025-11-16 12:19:33'),(231,99,7,NULL),(232,99,8,NULL),(233,100,4,'2025-11-16 12:21:44'),(234,100,5,'2025-11-16 12:21:29'),(235,100,7,NULL),(236,100,8,NULL),(237,101,4,'2025-11-16 12:21:44'),(238,101,5,'2025-11-16 12:21:38'),(239,101,7,NULL),(240,101,8,NULL),(241,102,4,'2025-11-29 05:03:33'),(242,102,5,'2025-11-29 05:03:38'),(243,102,7,NULL),(244,102,8,NULL);
/*!40000 ALTER TABLE `message_read` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `private_chat`
--

DROP TABLE IF EXISTS `private_chat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `private_chat` (
  `chat_id` int NOT NULL AUTO_INCREMENT,
  `user1` int NOT NULL,
  `user2` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`chat_id`),
  UNIQUE KEY `unique_pair` (`user1`,`user2`),
  KEY `user2` (`user2`),
  CONSTRAINT `private_chat_ibfk_1` FOREIGN KEY (`user1`) REFERENCES `userdata` (`user_id`),
  CONSTRAINT `private_chat_ibfk_2` FOREIGN KEY (`user2`) REFERENCES `userdata` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `private_chat`
--

LOCK TABLES `private_chat` WRITE;
/*!40000 ALTER TABLE `private_chat` DISABLE KEYS */;
INSERT INTO `private_chat` VALUES (1,5,4,'2025-11-13 17:05:22'),(2,5,6,'2025-11-13 17:05:37'),(3,4,6,'2025-11-13 18:15:26'),(4,7,4,'2025-11-14 10:22:11'),(5,7,6,'2025-11-14 10:22:59'),(6,8,4,'2025-11-15 13:02:53'),(7,5,7,'2025-11-16 12:17:47'),(8,5,8,'2025-11-16 12:18:12'),(9,9,5,'2025-11-18 11:58:46');
/*!40000 ALTER TABLE `private_chat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `private_message`
--

DROP TABLE IF EXISTS `private_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `private_message` (
  `id` int NOT NULL AUTO_INCREMENT,
  `chat_id` int NOT NULL,
  `sender_id` int NOT NULL,
  `content` text,
  `file_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `chat_id` (`chat_id`),
  KEY `sender_id` (`sender_id`),
  CONSTRAINT `private_message_ibfk_1` FOREIGN KEY (`chat_id`) REFERENCES `private_chat` (`chat_id`),
  CONSTRAINT `private_message_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `userdata` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `private_message`
--

LOCK TABLES `private_message` WRITE;
/*!40000 ALTER TABLE `private_message` DISABLE KEYS */;
INSERT INTO `private_message` VALUES (9,2,5,'hii',NULL,'2025-11-13 18:06:29'),(10,2,5,'hii',NULL,'2025-11-13 18:09:53'),(13,3,4,'hello',NULL,'2025-11-13 18:15:36'),(14,3,4,'👍',NULL,'2025-11-13 18:25:21'),(23,3,4,'😂',NULL,'2025-11-14 05:34:52'),(24,2,5,'Shared file: ANIL FINAL RESUME.pdf','/static\\uploads\\61a34fd6268541488f92ce48fdbcb40a.pdf','2025-11-14 05:46:57'),(25,4,7,'hello',NULL,'2025-11-14 10:22:17'),(26,4,7,'❤️',NULL,'2025-11-14 10:22:23'),(27,4,7,'Shared file: 61RNY9kOiyL._SX679_.jpg','/static\\uploads\\f728a3fb790249068d98d661d2800254.jpg','2025-11-14 10:22:36'),(28,4,7,'Shared file: Yogendra-Kavuluri-FlowCV-Resume-20251031 (1).pdf','/static\\uploads\\1535bdc85b514dd9b204248d3eb65279.pdf','2025-11-14 10:22:46'),(29,5,7,'hello',NULL,'2025-11-14 10:23:03'),(30,5,7,'🎉',NULL,'2025-11-14 10:23:08'),(35,2,5,'hello',NULL,'2025-11-14 18:16:42'),(36,2,5,'hiii',NULL,'2025-11-15 05:10:51'),(38,2,5,'zuasdfghj',NULL,'2025-11-15 11:16:55'),(39,2,5,'Shared file: 61N03oj9kyL._SY879_.jpg','/static\\uploads\\726c99694ce24c37bdfb04fd1b987a7e.jpg','2025-11-15 11:17:29'),(40,2,5,'😎',NULL,'2025-11-15 11:17:52');
/*!40000 ALTER TABLE `private_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `userdata`
--

DROP TABLE IF EXISTS `userdata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userdata` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `profile_pic` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `gender` varchar(10) NOT NULL DEFAULT 'male',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `userdata`
--

LOCK TABLES `userdata` WRITE;
/*!40000 ALTER TABLE `userdata` DISABLE KEYS */;
INSERT INTO `userdata` VALUES (4,'charan','saicharanthota3@gmail.com','$2b$12$rfgv14s39j3KxbXDjqL.FOwUX1z18VTTUHCIeyo9G6lt6hYsZmeZu','static\\uploads\\793fa4e6438b4d50a1d31b4c4c1c9c43.jpg','vijayawada','female'),(5,'yogendra','yogendrakavuluri8@gmail.com','$2b$12$8IJt7VooNMe/I.0/wZOlpOK1AWrvGpVzG3HsXK0HuDbVEqbNJ/f.i','static\\uploads\\c3fa0a95ccee48539200c68bf0ae819f.webp','vijayawada','male'),(6,'sathvika','pavulurisathvika533@gmail.com','$2b$12$oi6tTfM3oMlwkr8a5.G.7.QuvLZgYBtfytuB19hc0Q2qReUCWZosq',NULL,NULL,'male'),(7,'anil','banilgupta780@gmail.com','$2b$12$usbhe6OlplO3m5t/vtKG.OfQaK/OgOR6gDNLOURfyob8yb2uPRJyC',NULL,NULL,'male'),(8,'anusha ','anusha@codegnan.com','$2b$12$K1EeHZkqJ0ZFTLIuXk6CSOL3opxfexMnj6qIMPxL3WBUx6AOam7Vi','static\\uploads\\6137171c2eab4ff09bcb812ded04f118.jpg',NULL,'male'),(9,'surya','saisuryarajanala63@gmail.com','$2b$12$A0jIstHjKm8TS2kJaxppBumaTWx3xkC73EAiRakDFIh.knRCKGZeq',NULL,NULL,'male');
/*!40000 ALTER TABLE `userdata` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-30  9:36:08
