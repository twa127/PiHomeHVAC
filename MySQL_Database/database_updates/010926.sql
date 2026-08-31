ALTER TABLE `relays` RENAME COLUMN IF EXISTS previous_state to restore_state;
DROP TRIGGER IF EXISTS `before_relays_state_update`;
