ROSTI="CTRP310 CTRP311 CTRP850 CTRP312 CTRP851 CTRP852 CTRP100 CTRP105 CTRP303 CTRP106 CTRP304 CTRP700 CTRP107 CTRP305 CTRP701 CTRP108 CTRP702 CTRP101 CTRP102 CTRP300 CTRP103 CTRP301 CTRP104 CTRP302 CTRP707 CTRP307 CTRP703 CTRP308 CTRP704 CTRP309 CTRP705 CTRP706"

#ROSTI="CTRP111 CTRP853"

for e in $(echo $ROSTI); do
echo -e "\n\n\n\n####################### EXECUTANDO NO HOST $e"
/opt/jenkins/WAS/WebSphere/AppServer/bin/wsadmin.sh -host $e -lang jython -username admin -password @ppserver001 -f /opt/jenkins/WAS/scripts-automacao-job/deploy.py sofc-ear-frontoffice-validacional /opt/jenkins/WAS/scripts-automacao-job/tempear/sofc-ear-frontoffice-validacional-2.0.17.26.ear 

done
