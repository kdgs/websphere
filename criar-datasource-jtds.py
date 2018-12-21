import sys
import traceback
import time
import os

import threading
import time

import socket
import time, datetime
from java.lang import System
from java.util import Properties
from java.sql import Statement

import sys, getopt, java
import java.util as util
import java.io as javaio
import base64
import os
import os.path

# # Parâmetros de log de acordo com a específicação lá de casa

logLevel_TRACE = True;
logLevel_DEBUG = True;
logLevel_INFO = True;

global logLevel_TRACE, logLevel_DEBUG, logLevel_INFO;

# #
AMBIENTE = str(sys.argv)
#AMBIENTE = 'prod'
# # Tratamento de erro AdminUtilities
from com.ibm.ws.scripting import ScriptingException
failonerror = "false";
msgPrefix = "[CONFIG]";

# ## CACHE
global cacheNode;
cacheNode = None;

global jtdsProvider;
jtdsProvider = None;

global listaBases;
listaBases = [];

global t1, t2;


def tempoInicio():
    global t1;
    t1 = System.currentTimeMillis();


def tempoFim():
    global t1;
    global t2;
    t2 = System.currentTimeMillis();
    return str(t2 - t1) + "ms";


def horaLog():
    ts = time.time();
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S');


def info(Prefixo="N/A", Mensagem=None):
    nome = "INFO";
    global logLevel_INFO;
    if logLevel_INFO == True:
        msg = "[" + horaLog() + "] [" + nome + "] [" + Prefixo + "]: " + Mensagem;
        print msg;


def debug(Prefixo="N/A", Mensagem=None):
    nome = "DEBUG";
    global logLevel_DEBUG;
    if logLevel_DEBUG == True:
        msg = "[" + horaLog() + "] [" + nome + "] [" + Prefixo + "]: " + Mensagem;
        print msg;


def trace(Prefixo="N/A", Mensagem=None):
    nome = "TRACE";
    global logLevel_TRACE;
    if logLevel_TRACE == True:
        msg = "[" + horaLog() + "] [" + nome + "] [" + Prefixo + "]: " + Mensagem;
        print msg;


def erro(Prefixo="N/A", Mensagem=None):
    nome = "ERRO";
    msg = "[" + horaLog() + "] [" + nome + "] [" + Prefixo + "]: " + Mensagem;
    print msg;


def getNode():
    prefixo = "getNode";
    global cacheNode;
    try:
        if cacheNode is None:
            tempoInicio();
            trace(prefixo, "Executando AdminControl.getNode() - Tempo: " + tempoFim());
            cacheNode = AdminControl.getNode();
            debug(prefixo, "Nome do node obtido pela primeira vez");
            return cacheNode;
        else:
            debug(prefixo, "Node obtido do cacheNode");
            return cacheNode;
    except:
        print "[EXCEPTION]: %s %s " % (sys.exc_type, sys.exc_value)
        tipoExecpetion, val, traceBack = sys.exc_info()
        if (tipoExecpetion == SystemExit):  raise SystemExit, `val`
        else:
           AdminUtilities.fail(msgPrefix + AdminUtilities.getExceptionText(tipoExecpetion, val, traceBack), failonerror)
           

def getJTDSProvider():
    prefixo = "getJTDSProvider";
    global jtdsProvider;
    try:
        if jtdsProvider is None:
            tempoInicio();
            trace(prefixo, "Executando AdminConfig.getid(AdminControl.getCell()) - Tempo: " + tempoFim());
            jtdsProvider = AdminConfig.getid('/Cell:' + AdminControl.getCell() + '/JDBCProvider:jTDS - SQL Server/');
            debug(prefixo, "JDBCProvider JTDS obtido e armazenado");
            return jtdsProvider;
        else:
            debug(prefixo, "jtdsProvider obtido do cache jtdsProvider");
            return jtdsProvider;
    except:
        print "[EXCEPTION]: %s %s " % (sys.exc_type, sys.exc_value)
        tipoExecpetion, val, traceBack = sys.exc_info()
        if (tipoExecpetion == SystemExit):  raise SystemExit, `val`
        else:
           AdminUtilities.fail(msgPrefix + AdminUtilities.getExceptionText(tipoExecpetion, val, traceBack), failonerror)

           
def salvarConfiguracao():
    try:
        prefixo = "save";
        tempoInicio();
        AdminConfig.save();
        info(prefixo, "Salvar alterações - Tempo: " + tempoFim());
    except:
        print "[EXCEPTION]: %s %s " % (sys.exc_type, sys.exc_value)
        tipoExecpetion, val, traceBack = sys.exc_info()
        if (tipoExecpetion == SystemExit):  raise SystemExit, `val`
        else:
           AdminUtilities.fail(msgPrefix + AdminUtilities.getExceptionText(tipoExecpetion, val, traceBack), failonerror)


def reiniciarServidor():
    try:
        prefixo = "Restart"
        tempoInicio();
        AdminControl.invoke(AdminControl.queryNames('WebSphere:*,type=Server,node=' + getNode() + ',process=server'), 'restart')
        info(prefixo, "Reiniciando servidor - Tempo: " + tempoFim());
    except:
        print "[EXCEPTION]: %s %s " % (sys.exc_type, sys.exc_value)


def criarDatasourceJTDS(nomeDS, JNDI, servidorBanco, nomeBaseDados):
    tempoInicio();
    usuario = 'UsrAppJava'
    AliasUser = 'UsrAppJava'
    try:
        novoDatasource = AdminTask.createDatasource(jtdsProvider, '[-name ' + nomeDS + ' -jndiName ' + JNDI + ' \
        -dataStoreHelperClassName com.ibm.websphere.rsadapter.GenericDataStoreHelper \
        -description "Datasource de cooperativa JTDS"\
        -category "Cooperativa" \
        -containerManagedPersistence true -componentManagedAuthenticationAlias ' + usuario + ' -xaRecoveryAuthAlias ' + usuario + ' ]')
        
        AdminConfig.modify(novoDatasource, '[[connectionPool [[minConnections 0] \
        [connectionTimeout "3"] \
        [reapTime "15"] \
        [unusedTimeout "60"] \
        [maxConnections 100] \
        [purgePolicy "FailingConnectionOnly"]\
        [testConnectionInterval "1"]\
        [testConnection "true"]\
        ]]]');    
        
        AdminConfig.modify(novoDatasource, '[[logMissingTransactionContext "true"] [statementCacheSize "2000"]]')
    
        sqlCustomProperties = AdminConfig.create('J2EEResourcePropertySet', novoDatasource, [])
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, [['value', '1433'], ['name', 'portNumber'], ['type', 'java.lang.Integer']])
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, [['value', nomeBaseDados], ['name', 'databaseName'], ['type', 'java.lang.String']])
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, [['value', servidorBanco], ['name', 'serverName'], ['type', 'java.lang.String']]) 
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, [['value', 'true'], ['name', 'enable2Phase'], ['type', 'java.lang.String']])                            
        
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "enableMultithreadedAccessDetection"] [type "java.lang.Boolean"] [description ""] [value "false"] [required "false"]]')
        
        
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "preTestSQLString"] [type "java.lang.String"] [description ""] [value "SELECT 1"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "jmsOnePhaseOptimization"] [type "java.lang.Boolean"] [description ""] [value "false"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "reauthentication"] [type "java.lang.Boolean"] [description ""] [value "false"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "validateNewConnection"] [type "java.lang.Boolean"] [description ""] [value "true"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "validateNewConnectionRetryCount"] [type "java.lang.String"] [description ""] [value "2"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "validateNewConnectionRetryInterval"] [type "java.lang.String"] [description ""] [value "1"] [required "false"]]')                        
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "validateNewConnectionTimeout"] [type "java.lang.Integer"] [description ""] [value "2"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "errorDetectionModel"] [type "java.lang.String"] [description ""] [value "ExceptionMapping"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "nonTransactionalDataSource"] [type "java.lang.Boolean"] [description ""] [value "false"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "syncQueryTimeoutWithTransactionTimeout"] [type "java.lang.Boolean"] [description ""] [value "true"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "loginTimeout"] [type "java.lang.Integer"] [description ""] [value "5"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "lockTimeout"] [type "java.lang.Integer"] [description ""] [value "10000"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "webSphereDefaultQueryTimeout"] [type "java.lang.Integer"] [description ""] [value "18"] [required "false"]]')
        AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "socketTimeout"] [type "java.lang.Integer"] [description ""] [value "20"] [required "false"]]')
        info(nomeDS, "Recurso criado em: " + tempoFim());
    except:
        erro(nomeDS, "******** Falha ao criar o datasource " + nomeDS + " continuando.. ********");
        erro(nomeDS, "[EXCEPTION]: " + str(sys.exc_type) + str(sys.exc_value));
              
                
def removerZeroAEsquerda(valor):
    while valor[0] == "0":
        valor = valor[1:]
    return valor
                                                            
                    
def consultarCooperativasVIW_SERVIDOR():
    try:
	if AMBIENTE == "['prod']":
		URLBANCO='jdbc:sqlserver://SQLPROD19.sicoob.com.br:1433;databaseName=BDGerad;loginTimeout=5;sockettimeout=10'
		USRBANCO='usrsusan'
		PASBANCO='CacheMiss.2098'
        tempoInicio();
        prefixo = "ConsultaSQL";
        global listaBases;
        
        info(prefixo, "Acessando a 'viw_banco_servidor' para consultar as bases de cooperativa.");
        
        listaBases = [];
        
        props = Properties();
        props.put('user', USRBANCO);
        props.put('password', PASBANCO);
        trace(prefixo, "Carregando driver SQLJDBC42.JAR");
        sys.path.append('/opt/jenkins/WAS/scripts-automacao-job/jdbc/sqljdbc42.jar');
        import com.microsoft.sqlserver.jdbc.SQLServerDriver as Driver
        
        info(prefixo, "Abrindo conexão com a view de " + AMBIENTE );
        con = Driver().connect(URLBANCO, props);
        stmt = con.createStatement();
        resultSet = stmt.executeQuery("SELECT NomeBancoDados, substring(NomeServer,1,9) AS NomeServer, NumCooperativa FROM viw_banco_servidor WHERE NomeBancoDados like 'BDSicoob____'  OR NomeBancoDados like 'BDSicoobIntegracao'");
        while resultSet.next():
            nomeBD = resultSet.getString("NomeBancoDados");
            servidorBD = resultSet.getString("NomeServer");
            cooperativa = resultSet.getString("NumCooperativa");
            if cooperativa == "0":
                nomeDS = 'BancoobDS';
                JNDI = 'jdbc/BancoobDS';
            else:
                nomeDS = 'BancoobDS' + cooperativa;
                JNDI = 'jdbc/BancoobDS' + cooperativa;
               
            bdcoop = [nomeDS, JNDI, nomeBD, servidorBD, cooperativa];
            listaBases.append(bdcoop);
            # Trata excepcionalidades
#             if cooperativa == "0001":
#                 bdcoop = [nomeBD, servidorBD, ''];
#                 listaBases.append(bdcoop);
#                 bdcoop = [nomeBD, servidorBD, '1'];
#                 listaBases.append(bdcoop);
#             if cooperativa == "0002":
#                 bdcoop = [nomeBD, servidorBD, '2'];
#                 listaBases.append(bdcoop);
#             if cooperativa == "0001":
#                 bdcoop = [nomeBD, servidorBD, ''];
#                 listaBases.append(bdcoop);
#                 bdcoop = [nomeBD, servidorBD, '1'];
#                 listaBases.append(bdcoop);             
#             elif cooperativa == "0300":
#                 bdcoop = [nomeBD, servidorBD, '300'];
#                 listaBases.append(bdcoop);
#             else:
#                 listaBases.append(bdcoop);
        
        info(prefixo, "Bases de cooperativa consultadas com sucesso em " + tempoFim());
        info(prefixo, "Total de " + str(len(listaBases)) + " bases de cooperativas.");
    except:
        erro(prefixo, "******** Falha ao consultar VIW_BANCO_SERVIDOR **********");
        erro(prefixo, "[EXCEPTION]: " + str(sys.exc_type) + str(sys.exc_value));


try:
    inicio = System.currentTimeMillis();    
    getJTDSProvider();

    consultarCooperativasVIW_SERVIDOR();
    criados = 0;
    
    
    if AMBIENTE == "['prod']":
       for ds in listaBases:
          # 0       1       2       3               4
          # [nomeDS, JNDI, nomeBD, servidorBD, cooperativa];
           nomeDS = ds[0];
           JNDI = ds[1];
           nomeBD = ds[2];
           servidorBD = ds[3] + '.sicoob.com.br';
           cooperativa = ds[4];
        
           info("DS", nomeDS + " | " + JNDI + " | " + nomeBD + " | " + servidorBD + " | " + cooperativa);
           criarDatasourceJTDS(nomeDS, JNDI, servidorBD, nomeBD);
           criados = criados + 1;
           if criados > 30:
               salvarConfiguracao();
               criados = 0;        
        
       salvarConfiguracao();
       tempo = str((System.currentTimeMillis() - inicio) / 1000) + " segundos";
    #reiniciarServidor();
       info("FIM", "Datasources criados - tempo total: " + tempo);
    if AMBIENTE == "['hom']":
       print "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
#     
    
except:
    print "[EXCEPTION]: %s %s " % (sys.exc_type, sys.exc_value)  
    tipoExecpetion, val, traceBack = sys.exc_info()
    if (tipoExecpetion == SystemExit):  raise SystemExit, `val`
    else:
       AdminUtilities.fail(msgPrefix + AdminUtilities.getExceptionText(tipoExecpetion, val, traceBack), failonerror)


