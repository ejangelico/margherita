#!/usr/bin/perl
####!/opt/rh/python27/root/usr/bin/python

use Cwd; #  qw();  # o get current working directory
use File::Spec;
# http://search.cpan.org/~duncand/File-VirtualPath-1.011/lib/File/VirtualPath.pm
# get tar.gz, unpack, follow readme
use File::VirtualPath;

open F,"./setup";
@ln=<F>;
close F;

$cwd = Cwd::cwd();

# read parameters from setup file
for($m=0;$m<scalar(@ln);++$m) {
  if($ln[$m] =~ m/^\s*#/) {next;}      
  #
  if($ln[$m] =~ m/^shebang/) {
    $shebang = $ln[$m];
    $shebang =~ s/^[\w\s]+\:\s+(.+)\s+/$1/;
  }
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

# make directories
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
# system("cp ./templates/aliasdefs       ".$systemdir);
# system("cp ./templates/pvsdefs         ".$systemdir);
system("cp ./templates/setup_admin.py  ".$systemdir);
system("cp ./templates/setup_alias.py  ".$systemdir);
system("cp ./templates/setup_PVs.py    ".$systemdir);
system("cp ./templates/rrpv.py         ".$userdir);
system("cp ./templates/wrpv.py         ".$userdir);
#
# shebang line
opendir(DIR,$systemdir) or die $!;
while($file = readdir(DIR)) {
  $file=$systemdir.$file;
  if($file =~ m/\.py$/) {
    system("chmod a+w ".$file);
    system("chmod a+x ".$file);
    open P, $file;
    @pyf=<P>;
    close P;
    $pyf[0]="#".$shebang."\n"; # replace 1st line with shebang from file "setup"
#    $cmd = "chmod a+w ".$file;
    open P, ">".$file;
#    print $file."\n";  
    for($m=0;$m<scalar(@pyf);++$m) {print P $pyf[$m];}
    close P;  
  }
}
closedir(DIR);
##############
opendir(DIR,$userdir) or die $!;
while($file = readdir(DIR)) {
  $file=$userdir.$file;  
  if($file =~ m/\.py$/) {
    system("chmod a+w ".$file);
    system("chmod a+x ".$file);      
    open P, $file;
    @pyf=<P>;
    close P;
    $pyf[0]="#".$shebang."\n"; # replace 1st line with shebang from file "setup"
    open P, ">".$file;
#    print $file."\n";
    for($m=0;$m<scalar(@pyf);++$m) {
      print P $pyf[$m];
    }
    close P;
  }
}
closedir(DIR);

##############
sub getAbsPath {
 my ($in) = @_;
 my $p = File::VirtualPath->new();
 my $cwd=cwd();
 $p->path($cwd);
 $p->chdir($in);
# File::Spec->rel2abs($userdir);
 return $p->path_string()."/";
}
