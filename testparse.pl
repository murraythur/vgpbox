#!/usr/bin/perl

use strict;
use warnings;
use lib "/var/www/opdef.andybev.com";

use ADBOS::Parse;
use ADBOS::DB;
use Data::Dumper;

my $parser = ADBOS::Parse->new();

my $message = do { local $/; <STDIN> };

if (my $values =  $parser->parse($message))
{
#  my $shipid = $db->shipByName($values->{ship});
#  my $opdefs_id = $db->opdefStore($values, $shipid);
#  my $signals_id = $db->signalStore($values->{rawtext}, $opdefs_id, $values->{sitrep});
#  $db->signalAssociateOpdef($signals_id, $opdefs_id);
  
  print "Number year: $values->{number_year}\n";
  print "Number: $values->{number_serial}\n";

} else {
  print "Failed\n";
#  die "\n";
}


exit;
