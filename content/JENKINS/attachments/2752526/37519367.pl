#!/usr/bin/perl

my ($workspace, $baseDir, $prefix, $cyclomaticComplexity, $npathComplexity, $coupling);
$workspace = $ENV{'WORKSPACE'};
$jobName = $ENV{'JOB_NAME'};


if ($jobName = m/trunk\.codeanalysis\.([a-z]+)/) {
  $prefix = $1;
} else {
  die "no prefix specified";
}
print STDERR "team: $prefix\n";

# change this to the project the reports are fetched from
$baseDir="$workspace/pmd";
open(PMD, "<$baseDir/pmd_report_$prefix.xml")|| die "can not open PMD report $baseDir/pmd_report_$prefix.xml: $!";

while(<PMD>) {
  $cyclomaticComplexity += $1 if (/has a Cyclomatic Complexity of (\d+)/);
  $npathComplexity += $1 if (/has an NPath complexity of (\d+)/);
  $coupling += 1 if (/rule="CouplingBetweenObjects"/);
}

foreach('cyclomatic', 'npath', 'coupling') {
  open(OUT, ">$baseDir/pmd_plot_${team}_$_.properties")|| die "can not open output file: $!";

  print OUT "YVALUE=$cyclomaticComplexity\n" if /cyclomatic/;
  print OUT "YVALUE=$npathComplexity\n" if /npath/;
  print OUT "YVALUE=$coupling\n" if /coupling/;
}


