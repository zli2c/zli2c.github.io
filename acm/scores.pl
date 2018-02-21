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
<meta http-equiv="refresh" content="$refresh_time; scores.pl?refresh=$next_refresh_time$magicsuffix" />
</head>
<body>
|;

require "prefix.pl";

print "<h1>Scoreboard</h1>\n";

#print "<p>Will refresh in $refresh_time seconds. <a href=\"scores.pl?refresh=1$magicsuffix\">Refresh now</a>.</p>\n";

print qq|
<p><form name="counter">Will refresh in <input type="text" size="2" 
name="d2"> seconds. <a href=\"scores.pl?refresh=1$magicsuffix\">Refresh now</a>.</form></p>

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

my $when = isolocaltime();
my $elapsed = sectospan(isotimediff($when, $contest_start)+$refresh_time);
my $remaining = sectospan(isotimediff($contest_end, $when)-$refresh_time);

print "<p>Time Elapsed / Remaining: $elapsed / $remaining</p>\n";

print "<table>\n";

print "<tr><th>Position</th><th style=\"width:5em\">User</th>";
foreach (@problems) {
    print "<th style=\"width:6em\">Problem $_</th>";
}
print "<th>Solved</th><th>Total Time</th></tr>\n";

my $entries_string = `ls submissions/*/time`;
my @entries = split(/\s+/, $entries_string);
my %users = ();
foreach (@entries) {
    # I have no idea why this regex is working, but I'm not going to complain
    if (m{/(.+?)\.(.+?)\.(.+?)/}) {
        $users{$1} = 1;
    }
}
#print "Users: " . join(", ", sort keys %users) . "<br/>\n";

my %rows = ();
my %solved = ();
my %scores = ();
foreach my $user (keys %users) {
#print "<p>$user<ul>\n";
    my $score = 0;
    my $total = 0;
    my $penalty = 0;
    my $row = "<td>$user</td>";
    foreach my $problem (@problems) {
        my $submissions_string = `ls -rt submissions/$user.$problem.*/time 2> /dev/null`;
        my @submissions = split(/\s+/, $submissions_string);
        my $passed = 0;
        my $passtime = 0;
        my $passscore = 0;
        my $failed = 0;
        my $pending = 0;
        foreach (@submissions) {
            if (m{/(.+?)\.(.+?)\.(.+?)/}) {
                my $id = $3;
                my $status = readfile("submissions/$user.$problem.$id/status");
                $status =~ s{\s}{}g;
                if (-e "submissions/$user.$problem.$id/new") {
                    ++$pending;
                } elsif ($status eq "pass") {
                    ++$passed;
                    ++$total;
                    $passtime = readfile("submissions/$user.$problem.$id/time");
                    last;
                } else {
                    ++$failed;
                }
            } else { showdie("scores.pl $_"); }
        }
        if ($passed) {
            $passscore = isotimediff($passtime, $contest_start);
            $score += $passscore;
            $penalty += $failed * $submission_penalty;
        }
        my $q = "";
        if ($failed) { $q = "$failed"; }
        if ($pending) { $q = $q ne "" ? "$q+$pending?" : "$pending?"; }
        if ($q) { $q = " ($q)"; }
        my $passtext = $passed ? sectospan($passscore) : "&mdash;";
        $row .= "<td>$passtext$q</td>";
#print "<li>Problem $problem: passed $passed in $passscore @ $passtime, $failed failed, $pending pending</li>\n";
    }
    my $scoretime = sectospan($score);
#print "</ul>Total Problems: $total in $scoretime ($score)</p>\n";
    my $w = $penalty ? " + " . sectospan($penalty) : "";
    $row .= "<td>$total</td><td>$scoretime$w</td>";
    $rows{$user} = $row;
    $solved{$user} = $total;
    $scores{$user} = $score + $penalty;
}

my @orderedrows = ();
my $position = 0;
my $increment = 1;

my $now = -1;
foreach (reverse sort values %solved) {
    if ($_ == $now) { next; }
    $now = $_;
    
    my @theseusers = ();
    foreach (keys %users) {
        push @theseusers, $_ if $solved{$_} == $now;
    }

    my @orderedusers = sort { $scores{$a} <=> $scores{$b} } @theseusers;
    my $prevscore = -1;

    foreach $user (@orderedusers) {
        if ($scores{$user} == $prevscore) {
            ++$increment;
        } else {
            $position += $increment;
            $increment = 1;          
        }
        push @orderedrows, "<tr><td>$position</td>$rows{$user}</tr>\n";
    }

#    print "<p>$now: " . join (", ", @theseusers);
#    print "<p>$now: " . join (", ", @orderedusers);
}

foreach (@orderedrows) {
    print;
}

print "</table>\n";

print "<p>Problem Status Legend: Success Time (Failed + Pending?)</p>\n";

print "<p>Finished that one?  Go start another one of the <a href=\"problems.pl\">Problems</a>.</p>\n";

print "</body>\n</html>\n";

exit 0;

