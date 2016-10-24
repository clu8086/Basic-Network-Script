#!/usr/local/bin/bash

mkdir $(date +%d-%m-%y)
ne_number=`wc -l huawei_dslams.txt | awk '{print $1}'`;
for ((i=1; i<=ne_number; i++))
do
  IP=`sed -n "$i"p < huawei_dslams.txt | awk '{print $2}'`
  DSLAM=`sed -n "$i"p < huawei_dslams.txt | awk '{print $1}'`
  echo $DSLAM" "$IP
  ./huawei.pl $DSLAM $IP $(date +%d-%m-%y) &
done
cd $(date +%d-%m-%y)

echo "UNSUCCESSFUL CONNECTIONS" > ../SUMMARY
echo " " >> ../SUMMARY
cat ../err >> ../SUMMARY
echo " " >> ../SUMMARY
echo "ABNORMAL CONTROLLER STATUS" >> ../SUMMARY
echo " " >> ../SUMMARY
grep SCUN * | egrep -v 'Active_normal|Standby_normal' >> ../SUMMARY
echo " " >> ../SUMMARY
echo "SECOND CONTROLLER ACTIVE" >> ../SUMMARY
echo " " >> ../SUMMARY
grep 10.*Active * >> ../SUMMARY
echo " " >> ../SUMMARY
echo "CONTROLLER SYNC INCONSISTENCY" >> ../SUMMARY
echo " " >> ../SUMMARY
grep incompletely * | sed 's/\alarm, etc.)//g' >> ../SUMMARY
echo " " >> ../SUMMARY
echo "CPU HIGH" >> ../SUMMARY
echo " " >> ../SUMMARY
../cpu.sh >> ../SUMMARY
echo " " >> ../SUMMARY
echo "MEM HIGH" >> ../SUMMARY
echo " " >> ../SUMMARY
../mem.sh >> ../SUMMARY

mailx -s "[Preventive]::HUAWEI::DSLAM" DanubiusNOC-DE-BO-Fixed_ro@vodafone.com < ../SUMMARYl
