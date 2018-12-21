########################################################################
#                                                 			           #
# Criacao de resources                 			                       #
# Grupo Gerad App Server					                           #
#				                                                       #
########################################################################
import sys,getopt,java
import java.util as util
import java.io as javaio
import base64
import os
import os.path

lineSep = java.lang.System.getProperty('line.separator')

cell = 'wasbase'
node = 'cell'
serverName = 'server'
fileCli = '/opt/jenkins/WAS/scripts-automacao-job/configuracao-was.cli'
fileDs = '/opt/jenkins/WAS/scripts-automacao-job/ds-coop.txt'
FileExists = os.path.exists(fileCli)
File1Exists = os.path.exists(fileDs)
qtDS = 0
qtErrDS = 0
serverId = AdminConfig.getid('/Cell:'+cell+'/Node:'+node+'/Server:'+serverName+'/')
jvmId = AdminConfig.list('JavaVirtualMachine', serverId)
customJVM = 'false'
customOrb = 'false'
debugRemote = 'false'
passwordMailSessionProd = '03kM57XIZ'
passwordMailSessionTiHomol = '03kM57XIZ'
usuarioMailProd = 'SVCMail'
usuarioMailTiHomol = 'SVCMail'
ambiente = 'ti'
mssqlprovider = AdminConfig.getid('/Cell/'+cell+'/JDBCProvider:Microsoft SQL Server JDBC Driver/')
mssqlproviderxa = AdminConfig.getid('/Cell/'+cell+'/JDBCProvider:Microsoft SQL Server JDBC Driver (XA)/')
#db2provider = AdminConfig.getid('/Cell/'+cell+'/JDBCProvider:DB2 Universal JDBC Driver Provider/')
db2providerxa = AdminConfig.getid('/Cell/'+cell+'/JDBCProvider:DB2 Universal JDBC Driver Provider (XA)/')
dscoopprovider = AdminConfig.getid('/Cell/'+cell+'/JDBCProvider:Microsoft SQL Server JDBC Driver (XA)/')
jtdsProvider = AdminConfig.getid('/Cell/'+cell+'/JDBCProvider:jTDS - SQL Server/')
usuarioDS = 'usrcoopds'

if os.environ.get('jvm_xms') is not None:
	customJVM = 'true'
	jvm_xms = os.environ['jvm_xms']
        jvm_xmx = os.environ['jvm_xmx']
#        jvm_args = os.environ['jvm_args']

if os.environ.get('porta_orb') is not None:
	customOrb = 'true'
	orb_port = os.environ['porta_orb']

if os.environ.get('AMBIENTE') is not None:
	ambiente = os.environ['AMBIENTE']
if os.environ.get('debug_remote') is not None:
    debugRemote = os.environ['debug_remote']


print 'AMBIENTE: ' +ambiente
try:
###############################################################################################################################
        vJms = AdminTask.listWMQActivationSpecs(AdminConfig.getid( '/Cell:'+cell+'/')).split(lineSep)
        vJdbc = AdminConfig.list('DataSource', AdminConfig.getid( '/Cell:'+cell+'/')).split(lineSep)
#	vJdbcDB2 = AdminConfig.list('DataSource', AdminConfig.getid( '/Cell:'+cell+'/JDBCProvider:DB2 Universal JDBC Driver Provider/')).split(lineSep)
	vJdbcDB2XA = AdminConfig.list('DataSource', AdminConfig.getid( '/Cell:'+cell+'/JDBCProvider:DB2 Universal JDBC Driver Provider (XA)/')).split(lineSep)
	vJdbcMSSQL = AdminConfig.list('DataSource', AdminConfig.getid( '/Cell:'+cell+'/JDBCProvider:Microsoft SQL Server JDBC Driver/')).split(lineSep)
        vJdbcMSSQLXA = AdminConfig.list('DataSource', AdminConfig.getid( '/Cell:'+cell+'/JDBCProvider:Microsoft SQL Server JDBC Driver (XA)/')).split(lineSep)
        #print 'SAIDA DSCOOP' +vJdbcMSSQLXA
	vJdbcDSCOOP = AdminConfig.list('DataSource', AdminConfig.getid( '/Cell:'+cell+'/JDBCProvider:jTDS - SQL Server/')).split(lineSep)
	vJdbcDSCOOPJDBC = AdminConfig.list('DataSource', AdminConfig.getid( '/Cell:'+cell+'/JDBCProvider:Microsoft SQL Server JDBC Driver (XA)/')).split(lineSep)
        vJ2c = AdminConfig.list("JAASAuthData").split(lineSep)
	vListCustomProperties =  AdminConfig.list('Property', jvmId).split(lineSep)
	####### Customizacao porta ORB

	if customOrb == 'true':
		AdminTask.modifyServerPort('server1', '[-nodeName ' +node+ ' -endPointName ORB_LISTENER_ADDRESS -host * -port ' +orb_port+ ' -modifyShared true]')
	##### Cria Mail Session
	mailid = AdminConfig.getid('/Cell/wasbase/MailProvider:Built-in Mail Provider/MailSession:SicoobMail/') 
	if mailid == '':
		print 'Nao existe Mail Session configurado'
		print 'Iniciando configuracao mail session'
		if ambiente == 'prod':
			host_smtp = 'smtp.sicoob.com.br'
 			senhaMailSession = passwordMailSessionProd
			userMailSession = usuarioMailProd
		else:
			host_smtp = 'auth102.homologacao.com.br'
			senhaMailSession = passwordMailSessionTiHomol
			userMailSession = usuarioMailTiHomol
    
		AdminConfig.create('MailSession', AdminConfig.getid('/Cell/wasbase/MailProvider:Built-in Mail Provider/'), '[[name "SicoobMail"] [debug "false"] [mailStoreUser ""] [category ""] [mailTransportHost '+host_smtp+'] [jndiName "SicoobMailDS"] [mailTransportUser '+userMailSession+'] [mailStorePassword '+senhaMailSession+'] [mailStoreHost ""] [strict "true"] [description ""] [mailTransportPassword '+senhaMailSession+'] [mailFrom ""] [mailTransportProtocol "(cells/wasbase|resources.xml#builtin_smtp)"]]')

 
	####### Setando JVM Arguments

	if customJVM == 'true':
		if os.environ.get('jvm_args') is not None:
			jvm_args = os.environ['jvm_args']
			print 'XmX=' +jvm_xmx+ ' XmS=' +jvm_xms+ ' Argumentos JVM=' +jvm_args
			AdminTask.setJVMProperties('[-nodeName ' +node+ ' -serverName ' +serverName+ ' -verboseModeClass false -verboseModeGarbageCollection false -verboseModeJNI false -initialHeapSize ' +jvm_xms+ ' -maximumHeapSize ' +jvm_xmx+  ' -runHProf false -hprofArguments -debugMode false -debugArgs "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=7777" -executableJarFileName -genericJvmArguments "-Dlog4j.configuration=file:/opt/IBM/WAS/configApp/log/log.xml -Dfile.encoding=UTF8 -Duser.timezone=America/Sao_Paulo -Dbr.com.sicoob.mensageria.caminho=/mnt/mensageria/auditoria ' +jvm_args+  '" -disableJIT false]')
		else:
			print 'XmX=' +jvm_xmx+ ' XmS=' +jvm_xms
			AdminTask.setJVMProperties('[-nodeName ' +node+ ' -serverName ' +serverName+ ' -verboseModeClass false -verboseModeGarbageCollection false -verboseModeJNI false -initialHeapSize ' +jvm_xms+ ' -maximumHeapSize ' +jvm_xmx+  ' -runHProf false -hprofArguments -debugMode false -debugArgs "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=7777" -executableJarFileName -genericJvmArguments "-Dlog4j.configuration=file:/opt/IBM/WAS/configApp/log/log.xml -Dfile.encoding=UTF8 -Duser.timezone=America/Sao_Paulo -Dbr.com.sicoob.mensageria.caminho=/mnt/mensageria/auditoria" -disableJIT false]')
	####### Verificando necessidade de debug remoto

        if debugRemote == 'true':
		print 'Ativando Debug Remoto'
                AdminConfig.modify(jvmId, '[[debugMode "true"]]')

	####### Criando repositório federado

	if ambiente == 'prod':
		usuarioDS = 'usrappjava'
		baseEntry = "o=bancoob.br"
		Repository = "Bancoob"
		UniqueDistinguishedName = "o=bancoob.br"
		DistinguishedNameofaSubtree = "DC=bancoob,DC=br"
		existing_repos = AdminTask.listIdMgrRealmBaseEntries (['-name', AdminTask.listIdMgrRealms()])
		print "The existing User Repositories are: " + existing_repos
		repo_exists = existing_repos.find(baseEntry) != -1

		if repo_exists:
			print "Found the LDAP Repository [" + baseEntry + "]. Skipping creation."
		else:
			print "Creating the LDAP Repository..."
			print "Adding the base entry..."
			AdminTask.addIdMgrRepositoryBaseEntry(["-id", Repository, "-name", UniqueDistinguishedName, "-nameInRepository", DistinguishedNameofaSubtree])
			print "Adding the realm base entry..."
			AdminTask.addIdMgrRealmBaseEntry(["-name", "defaultWIMFileBasedRealm", "-baseEntry", UniqueDistinguishedName])
	else:
		baseEntry = "o=homologacao.com.br"
                Repository = "Homologacao"
                UniqueDistinguishedName = "o=homologacao.com.br"
                DistinguishedNameofaSubtree = "DC=homologacao,DC=com,DC=br"
                existing_repos = AdminTask.listIdMgrRealmBaseEntries (['-name', AdminTask.listIdMgrRealms()])
                print "The existing User Repositories are: " + existing_repos
                repo_exists = existing_repos.find(baseEntry) != -1

                if repo_exists:
                        print "Found the LDAP Repository [" + baseEntry + "]. Skipping creation."
                else:
                        print "Creating the LDAP Repository..."
                        print "Adding the base entry..."
                        AdminTask.addIdMgrRepositoryBaseEntry(["-id", Repository, "-name", UniqueDistinguishedName, "-nameInRepository", DistinguishedNameofaSubtree])
                        print "Adding the realm base entry..."
                        AdminTask.addIdMgrRealmBaseEntry(["-name", "defaultWIMFileBasedRealm", "-baseEntry", UniqueDistinguishedName])

	####### Removendo Variaveis de Ambiente
	for vCustomProperty in vListCustomProperties:
                if vCustomProperty:
			print "Removendo Variavel de ambiente  " +(vCustomProperty.split('(')[0])
                        AdminConfig.remove(vCustomProperty)

	#######  Removendo J2CAuth
        for j2c in vJ2c:
		if j2c:
			print "Removendo J2CAuth... " +j2c
			AdminConfig.remove(j2c)

        #######  Removendo DataSources...       
#        for datasources in vJdbcDB2:
#		print 'removendo datasources'
#		if datasources:
#			if not (datasources == "built-in-derby-datasource(cells/wasbase|resources.xml#DataSource_9007001)" or datasources == "DefaultEJBTimerDataSource(cells/wasbase/nodes/cell/servers/server1|resources.xml#DataSource_1000001)"):
#				print "Removendo DataSources...  " +datasources
#	                	AdminTask.deleteDatasource(datasources)

        for datasources in vJdbcDB2XA:
                if datasources:
                        if not (datasources == "built-in-derby-datasource(cells/wasbase|resources.xml#DataSource_9007001)" or datasources == "DefaultEJBTimerDataSource(cells/wasbase/nodes/cell/servers/server1|resources.xml#DataSource_1000001)"):
                                print "Removendo DataSources...  " +datasources
                                AdminTask.deleteDatasource(datasources)

        #for datasources in vJdbcMSSQL:
        #        if datasources:
        #                if not (datasources == "built-in-derby-datasource(cells/wasbase|resources.xml#DataSource_9007001)" or datasources == "DefaultEJBTimerDataSource(cells/wasbase/nodes/cell/servers/server1|resources.xml#DataSource_1000001)"):
        #                        print "Removendo DataSources...  " +datasources
        #                        AdminTask.deleteDatasource(datasources)

        #for datasources in vJdbcMSSQLXA:
        #        if datasources:
        #                if not (datasources == "built-in-derby-datasource(cells/wasbase|resources.xml#DataSource_9007001)" or datasources == "DefaultEJBTimerDataSource(cells/wasbase/nodes/cell/servers/server1|resources.xml#DataSource_1000001)"):
        #                        print "Removendo DataSources...  " +datasources
        #                        AdminTask.deleteDatasource(datasources)


        #######  Removendo Activation Specifications...
        for wmqas in vJms:
		if wmqas:
	                print "Removendo Activation Specification " +wmqas
	                AdminTask.deleteWMQActivationSpec(wmqas)


	if FileExists == 1:
		file = open(fileCli,'r')
		array = file.readlines()

		####### Criando Variaveis de ambiente
		for line in array:
		        if not (line.startswith("#") or line.startswith("type")):
		                line = line.rstrip()
		                if line:
		                        name = line.split('=', 1)[0]
		                        value = line.split('=', 1)[1]
					print "Criando Variavel " + name + "=" + value
					AdminConfig.create('Property', jvmId, '[[validationExpression ""] [name '+name+'] [description ""] [value '+value+'] [required "false"]]')
	
		for vDados in array:
			## Ignora comentários
			if not vDados.startswith("#"):
				## Tipo do resource
			        resourceType = (vDados.split(';')[0])
				## Ignora Linhas em branco
				if resourceType:
					## Criando activation specification
					if resourceType == 'type=AS':
					        name = (vDados.split(';')[1])
					        jndiname = (vDados.split(';')[2])
				        	destjndiname = (vDados.split(';')[3])
					        dstype = (vDados.split(';')[4])
					        msgselector = (vDados.split(';')[5])
					        qmname = (vDados.split(';')[6])
					        channel = (vDados.split(';')[7])
					        qmhost = (vDados.split(';')[8].rstrip())
				        	#port = (vDados.split(';')[9].rstrip())
				        	if dstype == "queue":
				                	dstype = "javax.jms.Queue"
					        if dstype == "topic":
					                dstype = "javax.jms.Topic"
						print "Criando AS " +name
					        #AdminTask.createWMQActivationSpec('"WebSphere MQ JMS Provider(cells/'+cell+'|resources.xml#builtin_mqprovider)"', '[-name '+name+' -jndiName '+jndiname+' -description -destinationJndiName '+destjndiname+' -destinationType '+dstype+' -messageSelector '+msgselector+' -qmgrName '+qmname+' -wmqTransportType CLIENT -qmgrSvrconnChannel '+channel+' -stopEndpointIfDeliveryFails false -qmgrHostname '+qmhost+' -qmgrPortNumber '+port+']')
					        AdminTask.createWMQActivationSpec('"WebSphere MQ JMS Provider(cells/'+cell+'|resources.xml#builtin_mqprovider)"', '[-name '+name+' -jndiName '+jndiname+' -description -destinationJndiName '+destjndiname+' -destinationType '+dstype+' -messageSelector '+msgselector+' -qmgrName '+qmname+' -wmqTransportType CLIENT -qmgrSvrconnChannel '+channel+' -stopEndpointIfDeliveryFails false -connectionNameList '+qmhost+ ']')
					
					## Criando queue connection factory
					if resourceType == "type=QCF":
						name = (vDados.split(';')[1])
			                        jndiname = (vDados.split(';')[2])
						qmname = (vDados.split(';')[3])
			                        channel = (vDados.split(';')[4])
			                        qmhost = (vDados.split(';')[5].rstrip()
			                        #port = (vDados.split(';')[6]).rstrip()
						obj = AdminConfig.getid('/Cell:'+cell+'/JMSProvider:WebSphere MQ JMS Provider/MQQueueConnectionFactory:'+ name +'/')
						if len(obj) == 0 :
		                                        print "QueueConnectionFactory nao existe .... "
		                                else:
		                                        AdminConfig.remove(obj)
						print "Criando Queue Connection Factory " + name
						#AdminTask.createWMQConnectionFactory('"WebSphere MQ JMS Provider(cells/'+cell+'|resources.xml#builtin_mqprovider)"', '[-type QCF -name '+name+' -jndiName '+jndiname+' -description -qmgrName '+qmname+' -wmqTransportType CLIENT -qmgrSvrconnChannel '+channel+' -qmgrHostname '+qmhost+' -qmgrPortNumber '+port+']')
						AdminTask.createWMQConnectionFactory('"WebSphere MQ JMS Provider(cells/'+cell+'|resources.xml#builtin_mqprovider)"', '[-type QCF -name '+name+' -jndiName '+jndiname+' -description -qmgrName '+qmname+' -wmqTransportType CLIENT -qmgrSvrconnChannel '+channel+' -connectionNameList '+qmhost+ ']')
		
					## Criando topic connection factory
					if resourceType == "type=TCF":
			                        name = (vDados.split(';')[1])
			                        jndiname = (vDados.split(';')[2])
			                        qmname = (vDados.split(';')[3])
			                        channel = (vDados.split(';')[4])
			                        qmhost = (vDados.split(';')[5].rstrip()
			                        #port = (vDados.split(';')[6]).rstrip()
						obj = AdminConfig.getid('/Cell:'+cell+'/JMSProvider:WebSphere MQ JMS Provider/MQTopicConnectionFactory:'+ name +'/')
						if len(obj) == 0 :
		                                        print "TopicConnectionFactory nao existe .... "
		                                else:
		                                        AdminConfig.remove(obj)
						print "Criando Topic Connection Factory " +name
			                        #AdminTask.createWMQConnectionFactory('"WebSphere MQ JMS Provider(cells/'+cell+'|resources.xml#builtin_mqprovider)"', '[-type TCF -name '+name+' -jndiName '+jndiname+' -description -qmgrName '+qmname+' -wmqTransportType CLIENT -qmgrSvrconnChannel '+channel+' -qmgrHostname '+qmhost+' -qmgrPortNumber '+port+']')
			                        AdminTask.createWMQConnectionFactory('"WebSphere MQ JMS Provider(cells/'+cell+'|resources.xml#builtin_mqprovider)"', '[-type TCF -name '+name+' -jndiName '+jndiname+' -description -qmgrName '+qmname+' -wmqTransportType CLIENT -qmgrSvrconnChannel '+channel+' -connectionNameList '+qmhost+ ']')
	
		
					## Criando queues	
					if resourceType == "type=QUEUE":
						name = (vDados.split(';')[1])
			                        jndiname = (vDados.split(';')[2])
						queuename = (vDados.split(';')[1])
						qmname = (vDados.split(';')[3]).rstrip()
		                                obj = AdminConfig.getid('/Cell:'+cell+'/JMSProvider:WebSphere MQ JMS Provider/MQQueue:'+name+'/')
		                                if len(obj) == 0 :
		                                        print "Queue nao existe .... "
		                                else:
		                                        AdminConfig.remove(obj)
		                                        print "Apagando Queue"
						print "Criando Queue " +name
						AdminTask.createWMQQueue(cell+'(cells/'+cell+'|cell.xml)', '[-name '+name+' -jndiName '+jndiname+' -queueName '+queuename+' -qmgr '+qmname+' -description ]')
		
					## Criando topicos
					if resourceType == "type=TOPIC":
			                        name = (vDados.split(';')[1])
			                        jndiname = (vDados.split(';')[2])
			                        topicname = (vDados.split(';')[1])
			                        qmname = (vDados.split(';')[3]).rstrip()
						obj = AdminConfig.getid('/Cell:'+cell+'/JMSProvider:WebSphere MQ JMS Provider/MQTopic:'+name+'/')
		                                if len(obj) == 0 :
		                                        print "Topic nao existe .... "
		                                else:
		                                        AdminConfig.remove(obj)
						print "Criando Topic " +name
						AdminTask.createWMQTopic(cell+'(cells/'+cell+'|cell.xml)', '[-name '+name+' -jndiName '+jndiname+' -topicName '+topicname+' -description -brokerDurSubQueue -brokerCCDurSubQueue -brokerPubQmgr '+qmname+' -brokerPubQueue ]')
		
					## Criando datasource db2 xa
		                       	if resourceType == "type=db2xa":
		                       		qntarray = len(vDados.split(';'))
                                        	if qntarray == 6:
                                                	portdb2 = '50001'
                                                	server = (vDados.split(';')[5]).strip()
                                        	if qntarray == 7:
                                                	server = (vDados.split(';')[5])
                                                	portdb2 = (vDados.split(';')[6]).strip()
						if qntarray > 7:
							server = (vDados.split(';')[5])
							portdb2 = (vDados.split(';')[6])
							if not portdb2:
								portdb2	= '50001'
								print "Definindo porta DB2 " + portdb2	
							minCon = (vDados.split(';')[7])
							maxCon = (vDados.split(';')[8])
                                        	name = (vDados.split(';')[1])
                                        	jndiname = (vDados.split(';')[2])
                                        	user = (vDados.split(';')[3])
                                        	base = (vDados.split(';')[4])
						print "Criando datasource DB2 XA:" +name
						ds = AdminTask.createDatasource(db2providerxa, '[-name ' +name+ ' -jndiName ' +jndiname+ ' -dataStoreHelperClassName com.ibm.websphere.rsadapter.DB2UniversalDataStoreHelper -containerManagedPersistence true -componentManagedAuthenticationAlias ' +user+  ' -xaRecoveryAuthAlias ' +user+ ' -configureResourceProperties [[databaseName java.lang.String ' +base+ '] [driverType java.lang.Integer 4] [serverName java.lang.String ' +server+ '] [portNumber java.lang.Integer ' +portdb2+ ']]]')
						qntarray = len(vDados.split(';'))
						if qntarray > 7:
							print "Redefinindo pool: " + name +': Min:' + minCon +',Max:' + maxCon
							AdminConfig.modify(ds, '[[connectionPool [[minConnections '+minCon+'] [maxConnections '+maxCon+'] [purgePolicy "EntirePool"]]]]')
						
						vProperty = AdminConfig.getid('/Cell/'+cell+'/JDBCProvider:DB2 Universal JDBC Driver Provider (XA)/DataSource:'+name+'/J2EEResourcePropertySet:/J2EEResourceProperty:webSphereDefaultIsolationLevel/')
						dsproperty = AdminConfig.getid('/Cell/'+cell+'/JDBCProvider:DB2 Universal JDBC Driver Provider (XA)/DataSource:'+name+'/J2EEResourcePropertySet:/')
						AdminConfig.modify(vProperty, [['value', 2], ['description', 'Specifies a default transaction isolation level for new connections. Resource References and Access Intents override this value. To configure a default transaction isolation level, use the constants defined by JDBC: 1 (READ UNCOMMITTED), 2 (READ COMMITTED), 4 (REPEATABLE READ), 8 (SERIALIZABLE)']])
						AdminConfig.create('J2EEResourceProperty', dsproperty, [['name', 'enable2Phase'], ['value', 'true'], ['type', 'java.lang.String']])
		
					## Criando datasource db2
					if resourceType == "type=db2":
		                               	qntarray = len(vDados.split(';'))
                                        	if qntarray == 6:
                                                	portdb2 = '50001'
                                                	server = (vDados.split(';')[5]).strip()
                                                if qntarray == 7:
                                                        server = (vDados.split(';')[5])
                                                        portdb2 = (vDados.split(';')[6]).strip()
                                                if qntarray > 7:
                                                        server = (vDados.split(';')[5])
                                                        portdb2 = (vDados.split(';')[6])
                                                        if not portdb2:
                                                                portdb2 = '50001'
                                                                print "Definindo porta DB2 " + portdb2
                                                        minCon = (vDados.split(';')[7])
                                                        maxCon = (vDados.split(';')[8]).rstrip()
                                        	name = (vDados.split(';')[1])
                                        	jndiname = (vDados.split(';')[2])
                                        	user = (vDados.split(';')[3])
                                        	base = (vDados.split(';')[4])
		                        	print "Criando datasource DB2 " +name
		                        	ds = AdminTask.createDatasource(db2provider, '[-name ' +name+ ' -jndiName ' +jndiname+ ' -dataStoreHelperClassName com.ibm.websphere.rsadapter.DB2UniversalDataStoreHelper -containerManagedPersistence true -componentManagedAuthenticationAlias ' +user+  ' -configureResourceProperties [[databaseName java.lang.String ' +base+ '] [driverType java.lang.Integer 4] [serverName java.lang.String ' +server+ '] [portNumber java.lang.Integer ' +portdb2+ ']]]')

                                                qntarray = len(vDados.split(';'))
                                                if qntarray > 7:
							print "Redefinindo pool: " + name +': Min:' + minCon +',Max:' + maxCon
							AdminConfig.modify(ds, '[[connectionPool [[minConnections '+minCon+'] [maxConnections '+maxCon+'] [purgePolicy "EntirePool"]]]]')
						vProperty = AdminConfig.getid('/Cell/'+cell+'/JDBCProvider:DB2 Universal JDBC Driver Provider/DataSource:'+name+'/J2EEResourcePropertySet:/J2EEResourceProperty:webSphereDefaultIsolationLevel/')
		                        	AdminConfig.modify(vProperty, [['value', 2], ['description', 'Specifies a default transaction isolation level for new connections. Resource References and Access Intents override this value. To configure a default transaction isolation level, use the constants defined by JDBC: 1 (READ UNCOMMITTED), 2 (READ COMMITTED), 4 (REPEATABLE READ), 8 (SERIALIZABLE)']])
					
					## Criando datasource mssql xa
		                        if resourceType == "type=mssqlxa":
		                                name = (vDados.split(';')[1])
		                                jndiname = (vDados.split(';')[2])
	        	                        user = (vDados.split(';')[3])
		                                base = (vDados.split(';')[4])
		                                server = (vDados.split(';')[5]).rstrip()
		                                print "Criando datasource MSSQL XA " +name
						AdminTask.createDatasource(mssqlproviderxa, '[-name ' +name+ ' -jndiName ' +jndiname+ ' -dataStoreHelperClassName com.ibm.websphere.rsadapter.MicrosoftSQLServerDataStoreHelper -containerManagedPersistence true -componentManagedAuthenticationAlias ' +user+  ' -xaRecoveryAuthAlias ' +user+ ' -configureResourceProperties [[databaseName java.lang.String ' +base+' ] [portNumber java.lang.Integer 1433] [serverName java.lang.String ' +server+ ']]]')
						dsproperty = AdminConfig.getid('/Cell/'+cell+'/JDBCProvider:Microsoft SQL Server JDBC Driver (XA)/DataSource:'+name+'/J2EEResourcePropertySet:/')
						AdminConfig.create('J2EEResourceProperty', dsproperty, [['name', 'enable2Phase'], ['value', 'true'], ['type', 'java.lang.String']])
					## Criando datasource mssql
		                        if resourceType == "type=mssql":
		                                name = (vDados.split(';')[1])
		                                jndiname = (vDados.split(';')[2])
		                                user = (vDados.split(';')[3])
		                                base = (vDados.split(';')[4])
		                                server = (vDados.split(';')[5]).rstrip()
		                                print "Criando datasource MSSQL " +name
		                                AdminTask.createDatasource(mssqlprovider, '[-name ' +name+ ' -jndiName ' +jndiname+ ' -dataStoreHelperClassName com.ibm.websphere.rsadapter.MicrosoftSQLServerDataStoreHelper -containerManagedPersistence true -componentManagedAuthenticationAlias ' +user+ ' -configureResourceProperties [[databaseName java.lang.String ' +base+' ] [portNumber java.lang.Integer 1433] [serverName java.lang.String ' +server+ ']]]')
		
					if resourceType == "type=j2cauth":
						password = ""
		                                name = (vDados.split(';')[1])
		                                passcrypt = (vDados.split(';')[2]).rstrip()
						for i in base64.decodestring(passcrypt):
						        password += chr(ord(i) ^ ord('_'))
		                                print "Criando J2CAuth " + name
						AdminTask.createAuthDataEntry('[-alias '+name+' -user '+name+' -password '+password+' -description ]')

					## Defini propriedades para DS	
					if resourceType == "type=customproperties":
						nameds = (vDados.split(';')[1])
						nameprop = (vDados.split(';')[2])
						valorprop = (vDados.split(';')[3])
						typeprop = (vDados.split(';')[4]).rstrip()
						DSsDB2 = AdminConfig.getid( '/DataSource:'+nameds+'')
						listprop = AdminConfig.showAttribute(DSsDB2,'propertySet')
						propertyList = AdminConfig.list('J2EEResourceProperty', listprop).splitlines()
						for dss in  propertyList:
							if dss.find(nameprop) != -1:
								sst = 'sss'
								print "Removendo propriedade:" +nameprop 
								AdminConfig.remove(dss)
						print "Criando propriedade customizada: " +nameprop +', Valor: ' + valorprop
						AdminConfig.create('J2EEResourceProperty', listprop , '[[name '+nameprop+'] [type "java.lang.'+typeprop+'" ] [description "Variavel criada atraves de propriedade definida no repositorio"] [value '+valorprop+'] [required "false"]]')

					## Defini TransactionTimeout
                                        if resourceType == "type=transactionService":
						TranTimeout = (vDados.split(';')[1])
						print "Configurando Transactiontimeout: " +TranTimeout 
						AdminConfig.modify('(cells/wasbase/nodes/cell/servers/server1|server.xml#TransactionService_1183122130078)', '[[totalTranLifetimeTimeout '+ TranTimeout +'] [httpProxyPrefix ""] [LPSHeuristicCompletion "ROLLBACK"] [httpsProxyPrefix ""] [wstxURLPrefixSpecified "false"] [enableFileLocking "true"] [enable "true"] [transactionLogDirectory "/opt/IBM/WAS/WebSphere/AppServer/profiles/AppSrv01/tranlog/wasbase/cell/server1/transaction;10M"] [enableProtocolSecurity "true"] [heuristicRetryWait "0"] [propogatedOrBMTTranLifetimeTimeout '+ TranTimeout +'] [enableLoggingForHeuristicReporting "false"] [asyncResponseTimeout "30"] [clientInactivityTimeout '+ TranTimeout +'] [heuristicRetryLimit "0"] [acceptHeuristicHazard "false"]]')

		AdminConfig.save();
                print 'Resources criados com sucesso!'

	else:
		print 'Arquivo configuracao-was.cli não encontrado.'

#	if File1Exists == 1:
#		if not ambiente == 'prod':
#			file1 = open(fileDs,'r')
#			array1 = file1.readlines()
#			for datasources in vJdbcDSCOOPJDBC:
#		                if datasources:
#				    print datasources
#		                        #if not (datasources == "built-in-derby-datasource(cells/wasbase|resources.xml#DataSource_9007001)" or datasources == "DefaultEJBTimerDataSource(cells/wasbase/nodes/cell/servers/server1|resources.xml#DataSource_1000001)"):
#		                    print "Removendo DataSources...  " +datasources
#		                    AdminTask.deleteDatasource(datasources)
#	
#			for vDscoop in array1:
#		                ## Ignora comentários
#		                if not vDscoop.startswith("#"):
#		                        ## Ignora linhas em branco
#					if vDscoop:
#			                        name = (vDscoop.split(';')[0])
#						jndiname = 'jdbc/'+name
#						server = (vDscoop.split(';')[1])
#						base = (vDscoop.split(';')[2]).rstrip()
#						user = usuarioDS
#						print "Criando datasource de cooperativa " +jndiname + " - usuario: " + usuarioDS
#						AdminTask.createDatasource(dscoopprovider, '[-name ' +name+ ' -jndiName ' +jndiname+ ' -dataStoreHelperClassName com.ibm.websphere.rsadapter.MicrosoftSQLServerDataStoreHelper -containerManagedPersistence true -componentManagedAuthenticationAlias ' +user+  ' -xaRecoveryAuthAlias ' +user+ ' -configureResourceProperties [[databaseName java.lang.String ' +base+' ] [portNumber java.lang.Integer 1433] [serverName java.lang.String ' +server+ ']]]')

        if File1Exists == 1:
               if not ambiente == 'prod':
                        file1 = open(fileDs,'r')
                        array1 = file1.readlines()
                        for datasources in vJdbcDSCOOP:
                                if datasources:
                                    print datasources
                                        #if not (datasources == "built-in-derby-datasource(cells/wasbase|resources.xml#DataSource_9007001)" or datasources == "DefaultEJBTimerDataSource(cells/wasbase/nodes/cell/servers/server1|resources.xml#DataSource_1000001)"):
                                    print "Removendo DataSources_jtds...  " +datasources
                                    AdminTask.deleteDatasource(datasources)

                        for vDscoop in array1:
                                ## Ignora comentários
                                if not vDscoop.startswith("#"):
                                        ## Ignora linhas em branco
                                        if vDscoop:
                                                name = (vDscoop.split(';')[0])
                                                jndiname = 'jdbc/'+name
                                                server = (vDscoop.split(';')[1])
                                                base = (vDscoop.split(';')[2]).rstrip()
                                                user = usuarioDS
						print "provider: " +jtdsProvider
                                                print "Criando datasource de cooperativa jtds " +jndiname + " - usuario: " + user
						nD = AdminTask.createDatasource(jtdsProvider, '[-name ' +name+ ' -jndiName ' +jndiname+ ' -dataStoreHelperClassName com.ibm.websphere.rsadapter.GenericDataStoreHelper -description "Datasource de cooperativa JTDS" -category "Cooperativa" -containerManagedPersistence true -componentManagedAuthenticationAlias ' + user + ' -xaRecoveryAuthAlias ' + user + ' ]')
						#AdminConfig.modify(nD, '[[connectionPool [[minConnections 0] \
					        #[connectionTimeout "3"] \
      						#[reapTime "15"] \
					        #[unusedTimeout "60"] \
					        #[maxConnections 100] \
					        #[purgePolicy "FailingConnectionOnly"]\
					        #[testConnectionInterval "1"]\
					        #[testConnection "true"]\
					        #]]]');
					        #AdminConfig.modify(nD, '[[logMissingTransactionContext "true"] [statementCacheSize "2000"]]')

					        #sqlCustomProperties = AdminConfig.create('J2EEResourcePropertySet', nD, [])
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, [['value', '1433'], ['name', 'portNumber'], ['type', 'java.lang.Integer']])
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, [['value', base], ['name', 'databaseName'], ['type', 'java.lang.String']])
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, [['value', server], ['name', 'serverName'], ['type', 'java.lang.String']])
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, [['value', 'true'], ['name', 'enable2Phase'], ['type', 'java.lang.String']])  
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "enableMultithreadedAccessDetection"] [type "java.lang.Boolean"] [description ""] [value "false"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "preTestSQLString"] [type "java.lang.String"] [description ""] [value "SELECT 1"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "jmsOnePhaseOptimization"] [type "java.lang.Boolean"] [description ""] [value "false"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "reauthentication"] [type "java.lang.Boolean"] [description ""] [value "false"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "validateNewConnection"] [type "java.lang.Boolean"] [description ""] [value "true"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "validateNewConnectionRetryCount"] [type "java.lang.String"] [description ""] [value "2"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "validateNewConnectionRetryInterval"] [type "java.lang.String"] [description ""] [value "1"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "validateNewConnectionTimeout"] [type "java.lang.Integer"] [description ""] [value "2"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "errorDetectionModel"] [type "java.lang.String"] [description ""] [value "ExceptionMapping"] [required "false"]]')
						#AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "nonTransactionalDataSource"] [type "java.lang.Boolean"] [description ""] [value "false"] [required "false"]]')
        					#AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "syncQueryTimeoutWithTransactionTimeout"] [type "java.lang.Boolean"] [description ""] [value "true"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "loginTimeout"] [type "java.lang.Integer"] [description ""] [value "5"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "lockTimeout"] [type "java.lang.Integer"] [description ""] [value "10000"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "webSphereDefaultQueryTimeout"] [type "java.lang.Integer"] [description ""] [value "18"] [required "false"]]')
					        #AdminConfig.create('J2EEResourceProperty', sqlCustomProperties, '[[name "socketTimeout"] [type "java.lang.Integer"] [description ""] [value "20"] [required "false"]]')	


               AdminConfig.save();
	       print 'DataSource de Cooperativas criados com sucesso!'

	else:
		print 'Arquivos ds-coop.txt não encontrado. '

	AdminConfig.save()	
	print '\n===============================\n'
	print 'Criacao de resources e datasources finalizada!'

except:
        print '\n===============================\n'
        print 'ERRO ENCONTRADO! Os resources não foram criados'
        traceback.print_exc()
        AdminConfig.save()
