#!/usr/bin/perl

# This function reads a exelem file and converts it to an ipelem file.
# This is problem specific in that basis function will be set to 1 and
# this is a 1D basis function.

# Only for nb=1 and nj=3 (3 coordinates)

$filename = $ARGV[0];
$exelemfile = "$filename.exelem";
$ipelemfile = "$filename.ipelem";

### Open exelem file ###
open EXELEM, "<$exelemfile" or die "\033[31mError: Can't open exelem file $exelemfile\033[0m ";

# pattern matching
# /a/ matches something with the letter a in it
# /a+/ matches something with one or more a's in it
# /a*/ matches something with zero or more a's in it
# /./ matches any character
# /\s/ matches whitespace
# /\w/ matches a word character
# /\s+hello.*/ would match things like "      hello bob"
# /go+gle/ gogle, google, gooogle
# /^hello/ would match "hello    asfabdf " but not match " asfd as hello"

# if ($bob == 1) # checks if bob is 1
# if ($bob =~ /hello/) # check if bob contains the characters "hello" in order

# Reading "Group name"
$line= <EXELEM>; # grab a line from the file
if ($line =~ / Group name:/){ # if the line matchs the " Group name:" pattern then execute the next bit
  $line=~/\s*Group name:\s*(\w*)\s*/i; # match white space (\s) then matches word characters (\w) then whitespace
  $group=$1; #$1 stores the infor from the 1st set of brackets, $2 would be 2nd set etc
}else{
  die "\033[31mError: \"Group name\" not found in exelem header\033[0m ";
}
#print "Group name: $group\n";

$NumberOfElems=0;
$line = <EXELEM>;
while ($line) {
    if ($line =~ /Element:\s*(\S*)\s*0\s*0/) {
	$NumberOfElems=$NumberOfElems+1; 
    }
    $line = <EXELEM>;
}

print "Total number of elements $NumberOfElems \n";

close EXELEM;

### Exporting to ipelem ## 
### Open ipelem file
open IPELEM, ">$ipelemfile" or die "\033[31mError: Can't open ipelem file\033[0m ";
open EXELEM, "<$exelemfile" or die "\033[31mError: Can't open exelem file\033[0m ";

### Write ipelem header
print IPELEM " CMISS Version 1.21 ipelem File Version 2\n";
print IPELEM " Heading: $group\n\n";
printf IPELEM " The number of elements is [%5d]: %5d\n",$NumberOfElems,$NumberOfElems;
$nj=3; #specific for 3 coordinates

#print "Enter the basis function number:";
#$nb = <STDIN>;
$nb = 1;
#$nb=4; #basis function=1

### Loop over elems
### Read exelem data
#$NumberOfElems=0;
$COUNT=0; #element number you want to start from

$line = <EXELEM>;
while ($line) {
    if ($line =~ /\s*Element:\s*(\S*)\s*0\s*0/) { #\S matches a non-whitespace character
	#$NumberOfElems=$NumberOfElems+1;
	$COUNT=$1; #$1 is the character from the 1st set of brackets
	print IPELEM "\n";
	printf IPELEM " Element number [%5d]: %5d\n",$COUNT,$COUNT;
	printf IPELEM " The number of geometric Xj-coordinates is [%1d]: %1d\n",$nj,$nj;
	for ($i=1;$i<=$nj;$i++){
	    printf IPELEM " The basis function type for geometric variable %1d is [%1d]: %1d\n",$i,$nb,$nb;
	}
    }
        if ($line =~ / Nodes:/) { #\S matches a non-whitespace character
	$nodes = <EXELEM>;
	chomp $nodes;
	printf IPELEM " Enter the 4 global numbers for basis %1d:$nodes\n",$nb;
        }
    $line = <EXELEM>;
}
### End Loop over elems
#print "Total number of elements $NumberOfElems \n";

### Close files
close IPELEM;
close EXELEM;


