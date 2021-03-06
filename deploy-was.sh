#!/bin/bash

ARTIFACT_ID=$1
VERSAO_ARTIFACT_ID=$2
GROUP_ID=$3
AMBIENTE=$4
NOMECLUSTER=$5
DIREAR="/opt/jenkins/WAS/scripts-automacao-job/tempear"
WSADMIN="/opt/jenkins/WAS/WebSphere/AppServer/bin/wsadmin.sh"
ERROR=""
URL_DELIVERY="http://delivery.sicoob.com.br/sicoob-entrega-continua/configuracoes-clusters"
USUARIO="admin	"
PASSWORD="@ppserver001"
DEPLOY_PYTHON="/opt/jenkins/WAS/scripts-automacao-job/deploy.py"

case $AMBIENTE in
TI)
        AMBIENTE="TI" ;;
HOMOLOGACAO)
        AMBIENTE="HOMOLOGACAO";;
PRODUCAO)
        AMBIENTE="PRODUCAO";;
esac

#CONSULTA NO DELIVERY QUAIS SERVIDORES DO CLUSTER QUE O DEPLOY SERA EXECUTADO
#SERVIDORES=$(curl -s --request GET "$URL_DELIVERY"/"$NOMECLUSTER"/ambientes/"$AMBIENTE"/hosts | jq '.resultado[] | "\(.hostname)"' | tr -d "\"" | grep -i TRNP301)
SERVIDORES=$(curl -s --request GET "$URL_DELIVERY"/"$NOMECLUSTER"/ambientes/"$AMBIENTE"/hosts | jq '.resultado[] | "\(.hostname)"' | tr -d "\"")

#ESCOLHE UM SERVIDOR DA LISTA PARA CONFIAR NO CERTIFICADO. ASSUME QUE TODOS OS SERVIDORES POSSUEM O MESMO CERTIFICADO
SERVIDOR_CERTIFICADO=$(echo $SERVIDORES  | awk -F " " '{print $1}')

#COMANDO PARA CONFIAR NO CERTIFICADO DO WEBSPHERE NAS CONEXOES REMOTAS COM WSADMIN
echo "Confiando no certificado dos servidores para a execução do wsadmin remotamente..."
/opt/jenkins/WAS/WebSphere/AppServer/profiles/AppSrv01/bin/retrieveSigners.sh -autoAcceptBootstrapSigner -quiet -host $SERVIDOR_CERTIFICADO -conntype SOAP -trace -user $USUARIO -password $PASSWORD

for LISTA in $(echo $SERVIDORES)
do
echo "INFO: Atualizando servidor $LISTA"
echo ""

echo "Servidores que serão atualizados:"
echo $SERVIDORES

#EXECUTA DEPLOY EM CADA SERVIDOR DE FORMA SEQUENCIAL
$WSADMIN -host $LISTA -lang jython -username $USUARIO -password $PASSWORD -f $DEPLOY_PYTHON "$ARTIFACT_ID" "$DIREAR"/"$ARTIFACT_ID"-"$VERSAO_ARTIFACT_ID".ear

if [ $? -eq 0 ]
then
        echo "INFO: Servidor atualizado com sucesso $LISTA"
        echo ""
	echo "INFO: Removendo ear de backup "$ARTIFACT_ID"-bkp.ear..."
	rm -f /tmp/"$ARTIFACT_ID"-bkp.ear
else
        echo "ERROR: Erro ao atualizar o servidor $LISTA"
        echo ""
        ERROR="Erro ao atualizar o servidor $LISTA\n$ERROR"
                echo "###### SERVIDORES COM ERRO DE DEPLOY ######"
                echo -e "$ERROR"
fi

done

echo "INFO: Deletando EAR's do diretório temporário $DIREAR"

if [ $? -eq 0 ]
then
	cd $DIREAR ; rm -f "$ARTIFACT_ID"-"$VERSAO_ARTIFACT_ID".ear
fi
