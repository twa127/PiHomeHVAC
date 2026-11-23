ALTER TABLE `relays` ADD COLUMN IF NOT EXISTS `previous_state` tinyint(1) DEFAULT '0' COMMENT '0 = OFF, 1 = ON' AFTER `user_display`;
