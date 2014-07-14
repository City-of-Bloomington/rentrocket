<?php
/**
 * @copyright 2014 City of Bloomington, Indiana
 * @license http://www.gnu.org/licenses/agpl.txt GNU/AGPL, see LICENSE.txt
 * @author Cliff Ingham <inghamn@bloomington.in.gov>
 */
include './configuration.inc';

$pdo = new PDO(DB_USER, DB_USER, DB_PASS, [PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);

$sql = 'select * from tblDistricts';

$result = $pdo->query($sql)->fetchAll();
foreach ($result as $row) {
	print_r($row);
}
