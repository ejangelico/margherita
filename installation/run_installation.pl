#!/usr/bin/perl

use Cwd; #  qw();  # o get current working directory
use File::Spec;
# http://search.cpan.org/~duncand/File-VirtualPath-1.011/lib/File/VirtualPath.pm
# get tar.gz, unpack, follow readme
use File::VirtualPath;

open F,"./setup";
@ln=<F>;
close F;

$cwd = Cwd::cwd();

for($m=0;$m<scalar(@ln);++$m) {
  if($ln[$m] =~ m/^\s*#/) {next;}      
  #
  if($ln[$m] =~ m/^username/) {
    $user=$ln[$m];
    $user =~ s/^[\w\s]+\:\s+(.+)\s+/$1/;
  }
  #
  if($ln[$m] =~ m/^database/) {
    $database=$ln[$m];
    $database =~ s/^[\w\s]+\:\s+(.+)\s+/$1/;
  }
  #
  if($ln[$m] =~ m/^user directory/) {
    $userdir=$ln[$m];
    $userdir =~ s/^[\w\s]+\:\s+(.+?)\/?\s*/$1\//;
#                                 ^ non-greedy to leave something to match \/?
    $userdir = getAbsPath($userdir);
  }
  #
  if($ln[$m] =~ m/^system directory/) {
    $systemdir=$ln[$m];
    $systemdir =~ s/^[\w\s]+\:\s+(.+?)\/?\s*/$1\//;
    $systemdir = getAbsPath($systemdir);  
  }
  #
  if($ln[$m] =~ m/^logging directory/) {
    $logdir=$ln[$m];
    $logdir =~ s/^[\w\s]+\:\s+(.+?)\/?\s*/$1\//;
    $logdir = getAbsPath($logdir);    
  }
  #
}

# print "user dir: ".$userdir."\n";
# exit;

if(defined($userdir)) {system("mkdir ".$userdir);} else {die "user directory is not defined";}
if(defined($systemdir)) {system("mkdir ".$systemdir);} else {die "system directory is not defined";}
if(defined($logdir)) {system("mkdir ".$logdir);} else {die "logging directory is not defined";}
system("cp ./templates/pvr.py ".$systemdir);
system("cp ./templates/pvw.py ".$systemdir);
##############
open F,">".$systemdir."userinfo";
print F $user."\n";
print F $database."\n";
close F;
open F,">".$userdir."userinfo";
print F $user."\n";
print F $database."\n";
close F;
##
open F,">".$systemdir."admindefs";
print F "HSpath, ".$systemdir."\n";
print F "logdir, ".$logdir."\n";
close F;
#
# system("cp ./templates/admindefs       ".$systemdir);
system("cp ./templates/aliasdefs       ".$systemdir);
system("cp ./templates/pvsdefs         ".$systemdir);
system("cp ./templates/setup_admin.py  ".$systemdir);
system("cp ./templates/setup_alias.py  ".$systemdir);
system("cp ./templates/setup_PVs.py    ".$systemdir);
system("cp ./templates/rrpv.py         ".$userdir);
system("cp ./templates/wrpv.py         ".$userdir);


sub getAbsPath {
 my ($in) = @_;
 my $p = File::VirtualPath->new();
 my $cwd=cwd();
 $p->path($cwd);
 $p->chdir($in);
# File::Spec->rel2abs($userdir);
 return $p->path_string()."/";
}
