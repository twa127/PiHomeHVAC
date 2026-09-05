ALTER TABLE `gateway_logs` ADD COLUMN IF NOT EXISTS `mqtt_disconnect` INT(11) NOT NULL DEFAULT '0' AFTER `pid_datetime`;
