import sys
import time
import os

import socket
import time, datetime

from com.ibm.ws.scripting import ScriptingException

def horaLog():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def info(Mensagem):
    msg = "[" + horaLog() + "] [INFO]: " + Mensagem
    print msg

def erro(Mensagem):
    msg = "[" + horaLog() + "] [ERRO]: " + Mensagem
    raise ValueError(msg)

# def obterNomeServidor():
#     try:
# #       nomeServidor = os.environ.get("HOSTNAME")
#         nomeServidor = socket.gethostname()
#         
#         if nomeServidor:
#             # Alguns servidores não tem FQDN wasx.xxx.xxx
#             if "." not in nomeServidor:
#                 return nomeServidor            
#             else:
#                 return nomeServidor.split('.')[0]
#         else:
#             erro("Não foi possível determinar o nome do servidor local")    
#     except Exception as e:
#         print(e)
#         erro("Falha ao obter HOSTNAME")
#################################


def validarParametrosEntrada():
    if sys.argv[0] is not None:
        if sys.argv[1] is not None:
            return True
        else:
            raise SystemExit


def removerVersaoAtual(aplicativo):
    
    appId = AdminConfig.getid("/Deployment:" + aplicativo + "/")
    
    if len(appId) > 0:
        info("O aplicativo já existe, removendo a versão atual")
        try:
#             backupEar = '/opt/configApp/earBkp/' + aplicativo
            backupEar = '/tmp/' + aplicativo + '-bkp.ear'
            info("Realizando backup do aplicativo..")
            AdminApp.export(aplicativo, backupEar)
            info("Removendo o aplicativo...")
            AdminApp.uninstall(aplicativo)
            
        except:
            erro("Falha ao remover o aplicativo atual!")
            typ, val, tb = sys.exc_info()
            print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
            return AdminUtilities.fail(AdminUtilities.getExceptionText(typ, val, tb), failonerror)
    else:
        info("Aplicativo não encontrado, executando primeira instalação")

def inciarAplicativo(aplicativo):
    try:
        statusAplicacao = AdminControl.completeObjectName('type=Application,name='+ aplicativo + ',*')

        if len(statusAplicacao) > 0:
            info("Aplicativo já iniciado!")
            return 'OK'
        else:
            info("Iniciando aplicativo... ")
            appManager = AdminControl.queryNames('name=ApplicationManager,*')
            AdminControl.invoke(appManager, 'startApplication', aplicativo)    
            return 'OK' 
    except:
        typ, val, tb = sys.exc_info()
        print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
        return AdminUtilities.fail(AdminUtilities.getExceptionText(typ, val, tb))
        
    
    
def instalarAplicativo(aplicativo):
    try:
        options = '[[.* .* default_host]]'
        AdminApp.install(earfile, '-appname "' + aplicativo + '" -cell ' + cell + ' -verbose -usedefaultbindings -update.ignore.old -MapWebModToVH ' + options)
        return 'OK'
    except:
        typ, val, tb = sys.exc_info()
        print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
        erro("Falha no deploy! Aplicativo: " + aplicativo +" Favor entrar em contato com a equipe responsável!")
        return AdminUtilities.fail(AdminUtilities.getExceptionText(typ, val, tb))
    

def mapearSharedLib():
    try:
       info("Incluindo biblitoecas compartilhadas")
       appManager = AdminControl.queryNames('name=ApplicationManager,*')
       AdminApp.edit(aplicativo, ['-MapSharedLibForMod', [['.*', '.*', 'SICOOB_LIBS']]])
       return 'OK'
    except: 
        typ, val, tb = sys.exc_info()
        print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
        return AdminUtilities.fail(AdminUtilities.getExceptionText(typ, val, tb))
    
    
def alterarClassLoader(aplicacacao):
    try:
        info("Alterando o ClassLoader para PARENT_LAST")
        vDeployment = AdminConfig.getid('/Deployment:' + aplicacacao + '/')
        vDeploymentObj = AdminConfig.showAttribute(vDeployment, 'deployedObject')
        vClassLoader = AdminConfig.showAttribute(vDeploymentObj, 'classloader')
        AdminConfig.modify(vClassLoader, [['mode', 'PARENT_LAST']])
        return 'OK'
    except: 
        typ, val, tb = sys.exc_info()
        print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
        return AdminUtilities.fail(AdminUtilities.getExceptionText(typ, val, tb))

def aguardarDeployApp(aplicacacao):
    try:
        info("Aguardando sincronização do EAR..")
        isAppReady = AdminApp.isAppReady(aplicativo)
        count = 0
        
        while (isAppReady == "false" and count < 90):
            time.sleep(1)
            isAppReady = AdminApp.isAppReady(aplicativo)
            count = count + 1
        
        isAppReady = AdminApp.isAppReady(aplicativo)
        
        if (isAppReady == "false"):
            erro("Falha durante a publicação do EAR")
            realizarRollback()
        
        return 'OK'
    except: 
        typ, val, tb = sys.exc_info()
        print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
        return AdminUtilities.fail(AdminUtilities.getExceptionText(typ, val, tb))

    
def realizarRollback():
    try:
        erro("Realizando rollback")
        AdminConfig.reset()
        AdminConfig.save()
        sys.exit(105)
    except: 
        typ, val, tb = sys.exc_info()
        print "Exception: %s %s " % (sys.exc_type, sys.exc_value)
        return AdminUtilities.fail(AdminUtilities.getExceptionText(typ, val, tb))
    
try:        
    validarParametrosEntrada()
    
    aplicativo = sys.argv[0]
    earfile = sys.argv[1]
    
    cell = AdminControl.getCell()
    
        
    info("Cell = " + cell)
    info("Aplicativo = " + aplicativo)
    
    
    removerVersaoAtual(aplicativo)
    
    if (instalarAplicativo(aplicativo) == 'OK'):
        AdminConfig.save()
        info("Aplicação instalada com sucesso")  
    
    if (aguardarDeployApp(aplicativo) == 'OK'):
        info("Aplicação publicada e sincronizada") 
    
    if (mapearSharedLib() == 'OK'):
        AdminConfig.save()
                
    if (alterarClassLoader(aplicativo) == 'OK'):
        AdminConfig.save()
            
    if (inciarAplicativo(aplicativo) == 'OK'):
        info("EAR iniciado")
    
except:
    typ, val, tb = sys.exc_info()
    print "Exception: %s %s " % (sys.exc_type, sys.exc_value)   
    AdminUtilities.fail(AdminUtilities.getExceptionText(typ, val, tb))
    erro("Erro durante o deploy, desfazendo qualquer alteração")
    realizarRollback()
  

