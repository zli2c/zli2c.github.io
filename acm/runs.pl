#!/usr/bin/env perl

require "common.pl";

print "Content-Type: text/html\r\n\r\n";

my %QUERY = ();
{
    my @pairs = split(/&/, $ENV{"QUERY_STRING"});
    foreach $pair (@pairs)
    {
        ($name, $value) = split(/=/, $pair);
        $value =~ tr/+/ /;
        $value =~ s/%(..)/pack("C", hex($1))/eg;
        $QUERY{$name} = $value;
    }
}

my $magic = $QUERY{'magic'};
my $magicsuffix = $magic ? "&magic=1" : "";

my $refresh_time = int($QUERY{'refresh'});
if ($refresh_time < 1) {
    $refresh_time = 1;
}
$refresh_time = int($refresh_time);
my $next_refresh_time = $refresh_time + int(($refresh_time+1)/2);
if ($magic) { $next_refresh_time = $refresh_time; }

print qq|
<html>
<head>
$htmltitle
<meta http-equiv="refresh" content="$refresh_time; runs.pl?refresh=$next_refresh_time$magicsuffix" />
</head>
<body>
|;

require "prefix.pl";

print "<h1>Run History</h1>\n";

#print "<p>Will refresh in $refresh_time seconds. <a href=\"runs.pl?refresh=1$magicsuffix\">Refresh now</a>.</p>\n";

print qq|
<p><form name="counter">Will refresh in <input type="text" size="2" 
name="d2"> seconds. <a href=\"runs.pl?refresh=1$magicsuffix\">Refresh now</a>.</form></p>

<script> 
<!-- 
var seconds=$refresh_time;
function display(){ 
    if (seconds < 0) { 
        seconds = 0; 
    } 
    document.counter.d2.value = seconds;
    if (seconds > 0) {
        --seconds;
        setTimeout("display()",1000) 
    }
} 
display() 
--> 
</script> 
|;

print "<p>Possible Results: " . join(", ", sort values %statustext) . ".</p>\n";

print "<p>Done here? Check the to <a href=\"scores.pl\">Scoreboard</a>.</p>\n";

print "<table>\n";

print "<tr><th style=\"width: 10em\">Time</th><th style=\"width: 5em\">User</th><th style=\"width: 2em\">Problem</th><th style=\"width: 5em\">File</th><th style=\"width: 10em\">Result</th><th></th><th style=\"width: 5em\">Time</th></tr>\n";

my $entries_string = `grep -H . submissions/*/time`;
my @entries = split(/\s+/, $entries_string);
my %times = ();
foreach (@entries) {
    my ($id, $stamp) = split(/:/, $_, 2);
    if ($id =~ m{/(.+?)\.(.+?)\.(.+?)/}) {
        $times{$stamp . "." . $3} = $1 . "." . $2;
    }
}

foreach (reverse sort keys %times) {
    my ($t, $i) = split(/\./, $_, 2);
    my ($u, $p) = split(/\./, $times{$_}, 2);
    my $r = readfile("submissions/$u.$p.$i/status");
    chomp($r);
    if ($statustext{$r}) { $r = $statustext{$r}; }
    my $f = readfile("submissions/$u.$p.$i/file");
    if ($ENV{'REMOTE_ADDR'} eq "" || $magic) { 
        print "<tr><td colspan=5>$i</td></tr>\n";
    }
    my $s = "";
    if (-e "submissions/$u.$p.$i/new") {
        $s = "(Tentative)" unless $r =~ m{yellow};
    }
    my $d = sectospan(isotimediff($t, $contest_start));
    print "<tr><td>$t</td><td>$u</td><td>$p</td><td>$f</td><td>$r</td><td>$s</td><td align=\"right\">$d</td></tr>\n";
}

print "</table>\n";

print "</body>\n</html>\n";

exit 0;

