<?php
$cookielist=array("Chocolate Chips and Chunks", "Oatmeal Raisin", "Chocolate Decadence", "Butterscotch Pecan", "Peanut Butter", "Peanut Butter Milk Chocolate", "Chocolate Medley", "White Chocolate Chip", "Milk Chocolate Oatmeal", "Smartie", "Mocha Cappuccino", "Dark Chocolate Cranberry", "White Chocolate Cranberry", "Kona", "Chocolate Chip Pecan", "Macadamia Dark Chocolate", "Macadamia White Chocolate", "White Chocolate Almond Oatmeal", "Chocolate Chips", "Chocolate with Cashew", "Oatmeal", "Raisin", "Jam filled", "Double Chocolate", "Triple Chocolate", "Tea Biscuit", "Almond", "Flaky Walnut");

$wstr="";
if (!isset($_COOKIE['cookie'])) {
	$countfile="utils/../../debug/cookiecounter";
        if ($fh = fopen($countfile,"r")) {
                if ($numcookies = fgets($fh)){
	                fclose($fh);
        	        if ($numcookies > 400 && $fh = fopen($countfile,"w")){
                	        fwrite($fh,$numcookies+1);
                        	fclose($fh);
	                }
		}
                setcookie('cookie',$cookielist[$numcookies%sizeof($cookielist)]." ".$numcookies,time()+60*60*24*365*20);
		$wstr=$wstr."set cookie ";
		$wstr=$wstr.$cookielist[$numcookies%sizeof($cookielist)]." ".$numcookies;
		$wstr=$wstr."\n";
        }
}

$wstr=$wstr.print_r($_REQUEST,TRUE);
$wstr=$wstr.print_r($_COOKIE,TRUE);
$wstr=$wstr.print_r($_SERVER,TRUE);
if ($fh = fopen("utils/../../debug/log", 'a')){
	fwrite($fh,$wstr);
	fclose($fh);
}
?>

