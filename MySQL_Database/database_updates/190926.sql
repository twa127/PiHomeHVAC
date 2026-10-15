ALTER TABLE `sensor_type` ADD COLUMN IF NOT EXISTS `decimal_places` TINYINT(4) NOT NULL DEFAULT '1' AFTER `type`;
ALTER TABLE `sensor_type` DROP IF EXISTS `operator`;
ALTER TABLE `sensor_type` ADD COLUMN IF NOT EXISTS `operator` CHAR(4) NOT NULL DEFAULT 'None' AFTER `decimal_places`;
ALTER TABLE `sensor_type` DROP IF EXISTS `factor`;
ALTER TABLE `sensor_type` ADD COLUMN IF NOT EXISTS `factor` INT(11) NOT NULL DEFAULT '0' AFTER `operator`;

INSERT INTO jobs (`job_name`, `script`, `enabled`, `log_it`, `time`, `output`, `datetime`)
SELECT 'check_tuya_bridge', '/var/www/cron/check_tuya_bridge.php', 0, 0, 60, '', now()
FROM DUAL
WHERE NOT EXISTS (
   SELECT 1
   FROM jobs
   WHERE script = '/var/www/cron/check_tuya_bridge.php'
);


