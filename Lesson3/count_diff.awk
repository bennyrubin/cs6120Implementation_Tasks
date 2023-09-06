#!/bin/bash 
awk -F',' '
  BEGIN {
    getline; # Skip the header line
    total_diff = 0;
  }
  {
    current_result = $3;
    getline; # Skip the next line
    next_result = $3;
    diff = current_result - next_result;
    total_diff += diff;
  }
  END {
    print "Total Difference:", total_diff;
  }
' 