CREATE TABLE IF NOT EXISTS `reset` (
`id` int(11) NOT NULL AUTO_INCREMENT,
`sync` tinyint(4) NOT NULL,
`purge` tinyint(4) NOT NULL COMMENT 'Mark For Deletion',
`status` tinyint(4) DEFAULT NULL,
`type` text DEFAULT NULL COMMENT 'WEB/MAN/AUTO',
`reset_count` int(4) NOT NULL,
`start_datetime` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
`end_datetime` timestamp NULL DEFAULT NULL,
PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20264 DEFAULT CHARSET=utf16 COLLATE=utf16_bin;

INSERT INTO jobs (`job_name`, `script`, `enabled`, `log_it`, `time`, `output`, `datetime`)
SELECT 'check_boiler_reset', '/var/www/cron/check_boiler_reset.php', 1, 0, 60, '', now()
FROM DUAL
WHERE NOT EXISTS (
   SELECT 1
   FROM jobs
   WHERE script = '/var/www/cron/check_boiler_reset.php'
);
