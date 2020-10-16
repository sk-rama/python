#!/usr/bin/awk -f

BEGIN { 
}

# this code is executed once for each line
{
print "420"$1;
}

END {
    print " - DONE - ";
}
