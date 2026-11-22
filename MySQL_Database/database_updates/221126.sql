UPDATE `jobs` SET `script` = "/var/www/cron/check_sc.py" WHERE `script` = "/var/www/cron/check_sc.php";
UPDATE `jobs` SET `script` = "/var/www/cron/check_gw.py" WHERE `script` = "/var/www/cron/check_gw.php";
