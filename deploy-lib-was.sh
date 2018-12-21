#!/bin/bash

NOMECLUSTER=$1
AMBIENTE=$2
DIRLIB="/opt/jenkins/WAS/scripts-automacao-job/templib/$NOMECLUSTER"
ERROR=""
URL_DELIVERY="http://delivery.sicoob.com.br/sicoob-entrega-continua/configuracoes-clusters"
MAVEN_HOME="/opt/jenkins/WAS/aplicativos-apoio/apache-maven-3.0.4/bin"
ARQUIVOPOM="pom-build.xml"
DIR_AUTOMACAO="/opt/jenkins/WAS/scripts-automacao-job"
USER=admin
PASSWORD=@ppserver001


function downloadGit() {
	mkdir -p $DIRLIB
	ARQUIVO=$1
	CAMINHO_MOVE=$2
	TOKEN_GIT=aE3FNBtFjFW-e6geTHeC
	URL=http://git.sicoob.com.br/Was_Base/"$NOMECLUSTER"/raw/master/$ARQUIVO
	request_status="$(curl -i --header "PRIVATE-TOKEN: $TOKEN_GIT" "$URL")"
	http_status=$(echo "$request_status" | grep HTTP |  awk '{print $2}')
	echo -e "\n''''''''''''''''''''''''''''''''''''''''"
	echo "Buscando arquivo pom-build.xml no GIT: $URL"
	echo "STATUS: $http_status"
	if [ $http_status != '200' ]; then
	        echo "Falha ao acessar $URL - código HTTP STATUS retorno: $http_status"
        	echo "Utilizando arquivo $CAMINHO_MOVE baixado anteriormente"
        	if [ ! -f $CAMINHO_MOVE ]; then
			echo "ERROR: Arquivo $CAMINHO_MOVE nao encontrado!"
			exit 1
        	fi
	else
		curl -o $CAMINHO_MOVE -X GET --header "PRIVATE-TOKEN: $TOKEN_GIT" "$URL"
		echo "Arquivo obtido com sucesso e salvo no diretório $CAMINHO_MOVE"
	fi         
}


function configPOM(){
        
	mkdir -p "$DIRLIB"/lib/cta
        mkdir -p "$DIRLIB"/lib/prt
        mkdir -p "$DIRLIB"/lib/sicoob
	
	echo -e "\n'''''''''''''''''''''''''''''''''''''''''''''''"
	echo "INFO: Baixando arquivo POM do cluster $NOMECLUSTER..."
	downloadGit $ARQUIVOPOM "$DIRLIB"/"$ARQUIVOPOM"

	echo -e "\n'''''''''''''''''''''''''''''''''''''''''''''''"
	echo "INFO: Executando download de libs de terceiro e framework..."
	cd $MAVEN_HOME 
	./mvn clean package -Pwas -f $DIRLIB/$ARQUIVOPOM
        STATUS_POM=$?
	if [ $STATUS_POM != 0 ]
		then
        	echo "ERRO: Ocorreu um erro ao tentar baixar o arquivo $ARQUIVOPOM no Nexus."
	fi
	cd $DIRLIB
	echo "INFO: Criando pasta "cta" na estrutura de diretórios de lib. O diretório deve sempre existir, vazio ou não é obrigatório em todos os servidores."   

        rm -f $ARQUIVOPOM
	echo -e "\n'''''''''''''''''''''''''''''''''''''''''''''''"
}

function consultaDelivery(){

	SERVIDORES=$(curl -s --request GET "$URL_DELIVERY"/"$NOMECLUSTER"/ambientes/"$AMBIENTE"/hosts | jq '.resultado[] | "\(.hostname)"' | tr -d "\"")
	QNT_SERVIDORES=$(echo $SERVIDORES | awk -F " " '{print NF}')
	STATUS_DELIVERY=$?
        if [ $STATUS_DELIVERY != 0 ]
		then
		echo "ERROR: Ocorreu um erro ao tentar consultar a url $URL_DELIVERY"
        	exit 1		

	fi				

	if [ -z "$SERVIDORES" ]
	then
        	echo "ERROR: Não houve retorno na consulta dos servidores no Delivery. Verique se o nome do cluster informado está correto ou se existem servidores cadastrados para este cluster informado, a lista pode estar retornando vazio!"
        exit 1
	fi
}


function verificaAmbiente(){

case $AMBIENTE in
TI)
        AMBIENTE="TI" ;;
HOMOLOGACAO)
        AMBIENTE="HOMOLOGACAO";;
PRODUCAO)
        AMBIENTE="PRODUCAO";;
esac

}

function copiaLib(){

	for LISTA in $(echo $SERVIDORES)
        do
	
        echo "INFO" Parando servidor de aplicação...
        sshpass -f /home/svc-jenkins/.cfgpass ssh -q -o StrictHostKeyChecking=no svc-jenkins@$LISTA "sudo -u svc-was /opt/IBM/WAS/WebSphere/AppServer/bin/stopServer.sh server -user $USER -password $PASSWORD" 

	echo "INFO: Excluindo as libs atuais do servidor... $LISTA"
	sshpass -f /home/svc-jenkins/.cfgpass ssh -q -o StrictHostKeyChecking=no svc-jenkins@$LISTA "rm -rf /opt/IBM/WAS/configApp/libApp/*"

	echo "INFO: Copiando libs para o servidor... $LISTA"
	sshpass -f /home/svc-jenkins/.cfgpass scp -o StrictHostKeyChecking=no -r $DIRLIB/lib/* svc-jenkins@$LISTA:/opt/IBM/WAS/configApp/libApp/

        echo "INFO" Inciando servidor de aplicação...
       sshpass -f /home/svc-jenkins/.cfgpass ssh -q -o StrictHostKeyChecking=no svc-jenkins@$LISTA "sudo -u svc-was /opt/IBM/WAS/WebSphere/AppServer/bin/startServer.sh server"    	
	
	STATUS_SCP=$?
        if [ $STATUS_SCP -eq 0 ]
		then
        	echo "INFO: Servidor atualizado com sucesso $LISTA"
		echo "INFO: Removendo diretório temporário de libs Jenkins"
		rm -rf $DIRLIB/*
        	echo ""
			else
        		echo ""
			
        		ERROR="ERROR: Erro ao atualizar o servidor $LISTA\n$ERROR"
	fi

done

			echo "###########################################"
  			echo "###### SERVIDORES COM ERRO DE DEPLOY DE LIB ######"
                        QNT_ERROS=$(echo -e $ERROR | grep "Erro ao atualizar o servidor" | wc -l)
                        echo -e "$ERROR"
			echo "INFO: Quantidade de servidores com erros: $QNT_ERROS"
			QNT_SUCESSO=$(($QNT_SERVIDORES - $QNT_ERROS))
			echo "INFO: Quantidade de servidores com sucesso: $QNT_SUCESSO"

		
			if [ $QNT_SERVIDORES -eq $QNT_ERROS ]
			then
				echo "FATAL: Nenhum servidor recebeu atualização de lib!"
				exit 1 
			fi
} 


verificaAmbiente
configPOM
consultaDelivery
copiaLib
