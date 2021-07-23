CREATE TABLE `polls` (
  `poll_id` int unsigned NOT NULL,
  `date` date NOT NULL,
  `pollster` varchar(255) NOT NULL,
  `sample_size` int unsigned NOT NULL,
  `margin_of_error` varchar(255),
  `demographic` varchar(255),
  `country` varchar(255) NOT NULL,
  `crosstabs_entered` varchar(255),
  `crosstabs_not_entered` varchar(255),
  `is_complete` bit(1) NOT NULL,
  `if_incomplete_emailed` bit(1),
  `Link` varchar(255) NOT NULL,
  `Notes` longtext,
  PRIMARY KEY (`poll_id`),
  KEY `pollster` (`pollster`),
  CONSTRAINT `r216mb5d` FOREIGN KEY (`pollster`) REFERENCES `pollsters` (`pollster`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `pollsters` (
  `pollster` varchar(255) NOT NULL,
  `538_rating` varchar(10),
  PRIMARY KEY (`pollster`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `questions` (
  `question_id` int unsigned NOT NULL,
  `question_text` longtext,
  `response_scale` longtext,
  PRIMARY KEY (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `regions` (
  `region` varchar(255) NOT NULL,
  `macro_region` varchar(255),
  `Population` int unsigned,
  PRIMARY KEY (`region`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `response_favorability` (
  `response` varchar(255) NOT NULL,
  `favorability` tinyint NOT NULL,
  PRIMARY KEY (`response`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `responses` (
  `poll_id` int unsigned NOT NULL,
  `question_id` int unsigned NOT NULL,
  `response` varchar(255) NOT NULL,
  `xtab1_var` varchar(255) NOT NULL,
  `xtab1_val` varchar(255) NOT NULL,
  `xtab2_var` varchar(255) NOT NULL,
  `xtab2_val` varchar(255) NOT NULL,
  `percentage` float NOT NULL,
  `notes` longtext,
  PRIMARY KEY (`poll_id`,`question_id`,`response`,`xtab1_var`,`xtab1_val`,`xtab2_var`,`xtab2_val`),
  KEY `poll_id` (`poll_id`),
  KEY `question_id` (`question_id`),
  KEY `response` (`response`),
  CONSTRAINT `8am15ch4` FOREIGN KEY (`poll_id`) REFERENCES `polls` (`poll_id`),
  CONSTRAINT `c5mgu7k6` FOREIGN KEY (`question_id`) REFERENCES `questions` (`question_id`),
  CONSTRAINT `sf0sq1jj` FOREIGN KEY (`response`) REFERENCES `response_favorability` (`response`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
