CREATE TABLE `polls` (
  `poll_id` int unsigned NOT NULL,
  `date` date NOT NULL,
  `pollster` longtext NOT NULL,
  `sample_size` int unsigned NOT NULL,
  `margin_of_error` longtext,
  `demographic` longtext,
  `country` longtext NOT NULL,
  `crosstabs_entered` longtext,
  `crosstabs_not_entered` longtext,
  `is_complete` bit(1) NOT NULL,
  `If incomplete, emailed?` longtext,
  `Link` longtext NOT NULL,
  `Notes` longtext,
  PRIMARY KEY (`poll_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `pollsters` (
  `pollster` longtext NOT NULL,
  `538 rating` longtext NOT NULL,
  PRIMARY KEY (`pollster`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `questions` (
  `question_id` int unsigned NOT NULL,
  `question_text` longtext NOT NULL,
  `response_scale` longtext,
  PRIMARY KEY (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `regions` (
  `region` longtext NOT NULL,
  `macro_region` longtext,
  `Population` int unsigned,
  PRIMARY KEY (`region`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `response_favorability` (
  `response` longtext NOT NULL,
  `favorability` int NOT NULL,
  PRIMARY KEY (`response`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;