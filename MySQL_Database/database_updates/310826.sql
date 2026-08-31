ALTER TABLE `relays` ADD COLUMN IF NOT EXISTS `previous_state` tinyint(1) DEFAULT '0' COMMENT '0 = OFF, 1 = ON' AFTER `user_display`;
DROP TRIGGER IF EXISTS `before_relays_state_update`;
DELIMITER //
CREATE TRIGGER `before_relays_state_update`
BEFORE UPDATE
ON `relays`
FOR EACH ROW
BEGIN
    IF OLD.`state` <> NEW.`state` THEN
        SET NEW.`previous_state` = OLD.`state`;
    END IF;
END//
DELIMITER ;

