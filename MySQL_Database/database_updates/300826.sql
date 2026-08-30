ALTER TABLE `db_cleanup` ADD COLUMN IF NOT EXISTS `status` TINYINT(4) NOT NULL AFTER `purge`;
ALTER TABLE `db_cleanup` ADD COLUMN IF NOT EXISTS `start_time` time NOT NULL AFTER `status`;
ALTER TABLE `db_cleanup` ADD COLUMN IF NOT EXISTS `result` TINYINT(4) NOT NULL AFTER `start_time`;
ALTER TABLE `db_cleanup` ADD COLUMN IF NOT EXISTS `last_run` DATETIME NOT NULL AFTER `result`;
UPDATE `db_cleanup` SET `status`= 1, `start_time` = '02:00';
DELETE FROM `jobs` WHERE `job_name` = 'db_cleanup';
