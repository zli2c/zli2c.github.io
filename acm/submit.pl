#!/usr/bin/env perl

print "Content-Type: text/html\r\n\r\n";

require "common.pl";

print qq~
<html>
<head>
$htmltitle
</head>
<body>
~;

require "prefix.pl";

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

unless ($QUERY{'submit'}) {
    print qq|
    <form action="submit.pl?submit=1" method="POST">
    <p>Username: <input name="username" /></p>
    <p>Problem: <select name="problem">
    <option value="">(select)</option>
|;
    foreach (@problems) {
        my $s = $QUERY{'problem'} eq $_ ? " SELECTED" : "";
        print "    <option value=\"$_\"$s>$_</option>\n";
    }
    print qq|    </select></p>
    <p>Filename: <select name="filename">
    <option value="">(select)</option>
|;
    foreach (sort keys %compilecommands) {
        print "    <option value=\"$_\">$_</option>\n"
    }
    print qq|    </select></p>
    <p>Source Code:<br/>
    <textarea name="code" cols="80" rows="10"></textarea></p>
    <p><input type="submit" value="Submit Solution" /></p>
    </form>
    |;
    print "<p>Don't want to submit? Check the <a href=\"scores.pl\">Scoreboard</a>.</p>\n";
} else {

    my %FORM = ();
    {
        # Read in text
        $ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;
        if ($ENV{'REQUEST_METHOD'} eq "POST")
        {
            my $buffer = "";
            read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});

            # Split information into name/value pairs
            @pairs = split(/&/, $buffer);
            foreach $pair (@pairs)
            {
                ($name, $value) = split(/=/, $pair);
                $value =~ tr/+/ /;
                $value =~ s/%(..)/pack("C", hex($1))/eg;
                $FORM{$name} = $value;
            }
        }
    }

    my $username = $FORM{'username'};
    print "<p>Username given as $FORM{'username'}...";
    unless ($username =~ m{^[[:alnum:]]+$}) {
        print "Bad format";
        exit 1;
    }
    {
        open(FILE, "<", "allowed_usernames.txt") || showdie("users");
        my @allowed = <FILE>;
        chomp(@allowed);
        close(FILE);
        my $found = 0;
        foreach (@allowed) {
            if ($_ eq $username) { $found = 1; }
        }
        unless ($found) {
            showdie("Not Authorized.");
        }
    }
    print "Ok.</p>\n";

    my $problem = $FORM{'problem'};
    print "<p>Submitting problem $problem...";
    {
        my $found = 0;
        foreach (@problems) {
            if ($_ eq $problem) {
                $found = 1;
            }
        }
        unless ($found) {
            showdie("Unknown.");
        }
    }
    print "Ok.</p>\n";

    my $filename = $FORM{'filename'};
    print "<p>Got filename $filename...";
    if ($compilecommands{$filename} eq "") {
        showdie("Unknown.");
    }
    print "Ok, will use $filename.</p>\n";

    my $id = $ENV{"UNIQUE_ID"};

    print "<p>Will record submission as $id.</p>";

    my $name = $username . "." . $problem . "." . $id;

    my $when = isolocaltime();
    print "<p>Saved $when.</p>\n";

    mkdir("submissions/$name") || showdie("mkdir");

    writefile("submissions/$name/status", "new");
    writefile("submissions/$name/new", "");

    writefile("submissions/$name/time", $when);
    writefile("submissions/$name/from", $ENV{'REMOTE_NAME'});

    writefile("submissions/$name/file", $filename);

    writefile("submissions/$name/$filename", $FORM{'code'});

    print "<p>Done.</p>\n";

    print "<p>Now check the <a href=\"runs.pl\">Run History</a>.</p>\n";

}

print "</body>\n</html>\n";

exit 0;

