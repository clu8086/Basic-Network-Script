#!/bin/bash

mkdir $(date +%F)
X=`wc -l dslams.txt | awk '{print $1}'`;
for ((i=1; i<=X; i++))
do
   IP=`sed -n "$i"p < dslams.txt | awk '{print $2}'`
   DSLAM=`sed -n "$i"p < dslams.txt | awk '{print $1}'`
   
   echo $IP
   echo $DSLAM
   
  (sleep 2; echo usename; sleep 2; echo password; sleep 2;echo "###commands###";) | telnet $IP >> $(date +%F)/$DSLAM

done
