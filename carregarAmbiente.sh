#!/bin/bash

###############################
# O execução do script segue a seguinte ordem:
# 1. validarDadosObrigatorios
# 2. setarVariaveis
# 3. obterVariaveisAmbiente
# 5. customizarIndex
# 6. se o AMBIENTE for 'dev' remove o appender do graylog
#     removerGraylog
# 7. se a variável USE_DSCOOP=true cria os datasources
#     de cooperativa criarDatasourceCooperativa
# 8. se a variável USE_CERT=true obtem os
#     certificados do GTI obterCertificados
###############################

###############################
# Função para logar a execução do script
# e recebe apenas um parâmetro 
#
# Ex.: log "String para logar"
###############################
log(){

    echo "[CARREGAR_AMBIENTE]  $1"
}

###############################
# Função utilizatária para baixar artefatos
# do git e recebe três parâmetros: 
# 1. URL do Git
# 2. Nome do arquivo para ser salvo na pasta /tmp
# 3. Boolean que indica se o download não ocorrer com 
#    sucesso o script termina com erro
#
# Ex.:  downloadGit "http://url.git" "variavies.properties" "false"
###############################
WAS_HOME="/opt/jenkins/WAS/WebSphere/AppServer"
LOGDIR="/opt/jenkins/WAS/scripts-automacao-job/logs"
LOGEXC="$LOGDIR/logexec"
LOGTMP="$LOGDIR/tmp_resource"
> $LOGEXC
ID_DELIVERY="$1"
GET_DELIVERY=$(wget -q -O $LOGDIR/G http://delivery.sicoob.com.br/sicoob-entrega-continua/configuracoes-clusters/$ID_DELIVERY)
AMB=$2
if [ $AMB == "TI" ]; then
	AMBIENTE="ti"
elif [ $AMB == "HOMOLOGACAO" ]; then
	AMBIENTE="hom"
elif [ $AMB == "PRODUCAO" ]; then
        AMBIENTE="prod"
fi
export AMBIENTE=$AMBIENTE
PROJETO_GIT=$(cat $LOGDIR/G | jq '.resultado' | grep -iw projetoGit | head -n1 | awk '{print$2}' | tr -d "\",")
	
USE_DSCOOP="$3"
#AMBIENTE=$2
#SERVIDORES=$(cat $LOGDIR/G | jq '.resultado' | grep -A1 -iw $AMBIENTE | grep hostname | awk '{print$2}' | tr -d "\",")
SERVIDORES="ctrd101 ctrd102"
USUARIO=$(cat /opt/jenkins/WAS/scripts-automacao-job/.app | head -n1)
PASSWORD=$(cat /opt/jenkins/WAS/scripts-automacao-job/.app | tail -n1)
downloadGit(){ 

    URL=$1
    CAMINHO_MOVE=$2

    log "Buscando arquivo no GIT: $URL"

    request_status="$(curl -s -i --header "PRIVATE-TOKEN: $TOKEN_GIT" "$URL")"
    #request_status="$(curl "$URL")"

    http_status=$(echo "$request_status" | grep HTTP |  awk '{print $2}')

    echo "STATUS: $http_status"

    if [ $http_status != '200' ]; then

        log "Falha ao acessar $URL - código HTTP STATUS retorno: $http_status"
        log "Utilizando arquivo $CAMINHO_MOVE baixado anteriormente"

        if [ ! -f $CAMINHO_MOVE ]; then

            log "ERROR: Arquivo $CAMINHO_MOVE nao encontrado.!"
            exit 1
        fi

    else

        curl -s -o $CAMINHO_MOVE -X GET --header "PRIVATE-TOKEN: $TOKEN_GIT" "$URL"
        #curl -o $CAMINHO_MOVE -X GET "$URL"
        
        log "Arquivo obtido com sucesso e salvo no diretório $CAMINHO_MOVE"
        
    fi         

}

###############################
# Função para que valida os dados obrigatórios
# PROJETO_GIT e WAS_HOME
###############################
validarDadosObrigatorios() {

    log "Validando variáveis obrigatórias"

    if [ -z "$PROJETO_GIT" ] || [ -z "$WAS_HOME" ]; then

        log "ERROR: Variável PROJETO_GIT ou WAS_HOME não setada."
        exit 1

    fi

    if [ -z "$jvm_xms" ] || [ -z "$jvm_xmx" ]; then

        log "Variável jvm_xms, jvm_xmx Variável jvm_args não setada. Usando valores pré definidos."
    fi

}

###############################
# Função que define a URL para requisições
# no aplicativo entrega contínua
###############################
obterUrlEntregaContinua(){

    if [ $AMBIENTE = "hom" ]; then

        AMBIENTE_REQ="HOMOLOGACAO"

    elif [ $AMBIENTE = "ti" ]; then

        AMBIENTE_REQ="TI"

    else

        AMBIENTE_REQ="DEV"

    fi

    URL_ENTREGA_CONTINUA="http://delivery.sicoob.com.br/sicoob-entrega-continua/datasources/configuracao/$PROJETO_GIT/$AMBIENTE_REQ"

}

###############################
# Função que seta as variáveis para a execução do script
# AMBIENTE, USE_DSCOOP, USE_CERT, TOKEN_GIT, STANDALONE_XML, INDEX_PADRAO
# ARQUIVO_VARIAVEIS_AMB, URL_GIT_VARIAVEIS_AMB, 
# ARQUIVO_DS_COOP, URL_GIT_DS_COOP
# ARQUIVO_CERTIFICADO, URL_GIT_CERTIFICADO
###############################
setarVariaveis(){

    log "Setando variáveis para execução do script"

    if [ -z "$AMBIENTE" ]; then

        log "A variável AMBIENTE não foi definida, utilizando DEV"
        AMBIENTE=dev

    fi

    if [ -z "$USE_DSCOOP" ]; then

        log "A variável USE_DSCOOP não foi definida, utilizando false"
        USE_DSCOOP=false

    fi

    if [ -z "$USE_CERT" ]; then

        log "A variável USE_CERT não foi definida, utilizando false"
        USE_CERT=false

    fi

    
    LOG_HOST_TI="coletordev.homologacao.com.br"
    LOG_HOST_HOM="coletorhom.homologacao.com.br"
    LOG_HOST_PROD="coletorprod.sicoob.com.br"
    LOG_PORT="1514"
    SERVIDOR_APLICACAO="was"
    CERTS=${AMBIENTE}-certificados.zip

    if [ $AMBIENTE = "hom" ]; then

        export LOG_HOST=$LOG_HOST_HOM

    elif [ $AMBIENTE = "ti" ]; then

        export LOG_HOST=$LOG_HOST_TI

    else

        export LOG_HOST=$LOG_HOST_PROD

    fi

    LOG_HOST_NAME=$LOG_HOST
    PATH_WAS=$WAS_HOME/bin
    PATH_PROFILE=$WAS_HOME/profiles/sicoob
    PATH_CONFIG_APP="/opt/jenkins/WAS/scripts-automacao-job"    
    PATH_SCRIPT=$PATH_CONFIG_APP
    PATH_CERTS="/etc/ssl/sicoob/"
    
    TOKEN_GIT=aE3FNBtFjFW-e6geTHeC
    #TOKEN_GIT=Nudb4KhBAHJujsoSpgWv
        
    ARQUIVO_LOG=log.xml
    URL_GIT_LOG=http://git.sicoob.com.br/Was_Base/$PROJETO_GIT/raw/master/$ARQUIVO_LOG
    CAMINHO_ARQUIVO_LOG_TMP=$PATH_CONFIG_APP/log/log_tmp.xml
    CAMINHO_ARQUIVO_LOG=$PATH_CONFIG_APP/log/log.xml

    ARQUIVO_CLI=$AMBIENTE.parametros.conf 
    URL_GIT_CLI=http://git.sicoob.com.br/Was_Base/$PROJETO_GIT/raw/master/$ARQUIVO_CLI
    URL_GIT_CERTS=http://git.sicoob.com.br/Was_Base/$PROJETO_GIT/raw/master/$CERTS
    CAMINHO_ARQUIVO_CLI=$PATH_CONFIG_APP/configuracao-was.cli

    ARQUIVO_DS_COOP=$AMBIENTE-ds-coop.txt
    URL_GIT_DS_COOP=http://git.sicoob.com.br/Docker/gerad-was-base/raw/master/$ARQUIVO_DS_COOP
    CAMINHO_ARQUIVO_COOP=$PATH_CONFIG_APP/ds-coop.txt

    URL_GIT_TRUSTSTORE=http://git.sicoob.com.br/Docker/gerad-was-base/raw/master/trust.p12
    ARQUIVO_TRUSTSTORE=$PATH_PROFILE/config/cells/wasbase/nodes/cell/trust.p12

    URL_GIT_SCRIPT_RESOURCES=http://git.sicoob.com.br/Was_Base/gerad-was-base/raw/master/jvm/scripts/createResources.py
    ARQUIVO_SCRIPT_RESOURCES=$PATH_CONFIG_APP/jvm/scripts/createResources.py
    
    #definindo URL de entrega contínu
    obterUrlEntregaContinua
}

###############################
# Função que obtem os arquivos de propriedades do GIT.
# Se o download não ocorrer com sucesso deve utilizar o
# arquivo já baixado anteriormente, porém se o arquivo
# não existir termina o script com erro
###############################


###############################
# Função que escreve o arquivo de DS de coop
# e implanta no diretório /deployments
###############################
escreverArquivoDatasource(){

    log "Escrevendo arquivo de Datasource:"

    QTDE=$1

    INDICE=0
    while [ $INDICE -lt $QTDE ] 
    do

        DSCOOP=$(cat $WAS_HOME/$AMBIENTE-ds-coop.json | jq --raw-output  ".resultado[$INDICE] .dsCooperativa")
        SRVSQL=$(cat $WAS_HOME/$AMBIENTE-ds-coop.json | jq --raw-output  ".resultado[$INDICE] .servidor")
        BD=$(cat $WAS_HOME/$AMBIENTE-ds-coop.json | jq --raw-output  ".resultado[$INDICE] .database")

        log "DS COOP: $DSCOOP $SRVSQL $BD"

        echo "$DSCOOP;$SRVSQL;$BD" >>  $CAMINHO_ARQUIVO_COOP

    INDICE=$((INDICE+1))
    done     
}

###############################
# Função que cria os datasources de cooperativa:
# 1. Se o AMBIENTE for prod, relaiza download do arquivo no GIT
#    se o download ocorrer com sucesso move o arquivo para o diretório deployments
#    se o download ocorrer com falha utiliza uma versão já baixada anteiormente
# 2. Se o ambiente for ti, hom ou dev realiza uma chamada REST para o aplicativo
#    /sicoob-entrega-continua e gera dinamicamente o XML de Datasources
###############################
criarDatasourceCooperativa(){
SRV=$1
    log "Criando Datasource de Cooperativas para o ambiente: $AMBIENTE"

    if [ $AMBIENTE = "prod" ]; then
	/opt/jenkins/WAS/WebSphere/AppServer/bin/wsadmin.sh -username $USUARIO -password $PASSWORD -host $SRV -lang jython -conntype SOAP -f $PATH_SCRIPT/criar-datasource-jtds.py $AMBIENTE
        #rm /opt/IBM/WAS/WebSphere/AppServer/profiles/sicoob/config/cells/wasbase/resources.xml
        #downloadGit http://git.sicoob.com.br/Was_Base/gerad-was-base/raw/master/resources.xml /opt/IBM/WAS/WebSphere/AppServer/profiles/sicoob/config/cells/wasbase/resources.xml

    else

        log "Obtendo Datasources cadastrados em: $URL_ENTREGA_CONTINUA"

        wget -q "$URL_ENTREGA_CONTINUA" -O $WAS_HOME/$AMBIENTE-ds-coop.json -T 10 2>&1 
        
        qtde=$(cat $WAS_HOME/$AMBIENTE-ds-coop.json | jq '.resultado[] .dsCooperativa' | wc -l)

        log "Quantidade de Datasources cadastrados: $qtde"

        if [ $qtde -gt "0" ]; then
            
            escreverArquivoDatasource $qtde

        fi 

        rm $WAS_HOME/$AMBIENTE-ds-coop.json       
    fi    
}

copiaCertificados(){
    
    log "Copiando certificados"
    mkdir -p $PATH_CERTS
    rm -rf $PATH_CERTS/*
    downloadGit $URL_GIT_CERTS $PATH_CERTS$CERTS
    unzip $PATH_CERTS/$CERTS -d $PATH_CERTS
    rm -rf $PATH_CERTS/$CERTS
    echo "Certificados adicionados."
    
}

copiaTrustStore(){

   log "Copiando TrustStore"
   downloadGit $URL_GIT_TRUSTSTORE $ARQUIVO_TRUSTSTORE

}

###############################
# Função que cria todos os demais recursos do servidor: Fila, Tópico, Datasource
###############################
criarRecursos(){
TTERRO=0

#    log "Criando Recursos para o ambiente: $AMBIENTE"

    downloadGit $URL_GIT_CLI $CAMINHO_ARQUIVO_CLI
	for SRV in $(echo $SERVIDORES); do
		if [ $USE_DSCOOP = "true" ]; then
	log "Criando Recursos para o servidor $SRV" 
 		  criarDatasourceCooperativa $SRV

		fi
  #EXCCOM=$(/opt/jenkins/WAS/WebSphere/AppServer/bin/wsadmin.sh -username $USUARIO -password $PASSWORD -host $SRV -lang jython -conntype SOAP -f $PATH_SCRIPT/createResources.py)
  /opt/jenkins/WAS/WebSphere/AppServer/bin/wsadmin.sh -username $USUARIO -password $PASSWORD -host $SRV -lang jython -conntype SOAP -f $PATH_SCRIPT/createResources.py
  RC=$?
#echo "VALOR RETORNO: " $RC
  	if [ "$RC" -eq "0" ]; then
   	    echo "Propriedades definidas com sucesso no servidor: " $SRV | tee $LOGTMP
	    echo ""
    	else
	    echo "Falha na execução no servidor: "$SRV | tee $LOGTMP
		TTERRO=$((TTERRO+1))
		#echo "Quantidade de erros: " $TTERRO	
    echo ""
	fi
	cat $LOGTMP >> $LOGEXC
	echo "Quantidade de erros: " $TTERRO    
#    cat $CAMINHO_ARQUIVO_CLI | grep -v "type" | grep -v "#"
	if [ -e $CAMINHO_ARQUIVO_COOP ]; then
    rm $CAMINHO_ARQUIVO_COOP
	fi
done
    rm $CAMINHO_ARQUIVO_CLI
}

buscarArquivoLog(){

    log "Configurando log."

    downloadGit $URL_GIT_LOG $CAMINHO_ARQUIVO_LOG_TMP
    
    envsubst < $CAMINHO_ARQUIVO_LOG_TMP > $CAMINHO_ARQUIVO_LOG

    rm $CAMINHO_ARQUIVO_LOG_TMP

}


copiaScriptResources(){

    log "Baixando script createResources.py"

    downloadGit $URL_GIT_SCRIPT_RESOURCES $ARQUIVO_SCRIPT_RESOURCES

}
validarDadosObrigatorios

setarVariaveis

#copiaScriptResources

#if [ $USE_DSCOOP = "true" ]; then

 #  criarDatasourceCooperativa
   
#fi

if [ $USE_CERT = "true" ]; then

   copiaCertificados
   
fi   

if [ $PROJETO_GIT != "gerad-was-base" ]; then

    criarRecursos
    #buscarArquivoLog
    #copiaTrustStore
fi


log "Fim da execução do script."
log "Resultado:"
echo "##########################################################"
cat $LOGEXC
echo "##########################################################"
exit $TTERRO
