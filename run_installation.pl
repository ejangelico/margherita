#!/usr/bin/perl

use Cwd;

# system("./clean.pl");
system("cp ./CustomFilesForMargherita/C3PO/* ./C3PO/");
system("cp ./CustomFilesForMargherita/user/* ./user/");
system("cd installation; ./run_installation.pl");
#
system("cd C3PO; ./setup_all");
