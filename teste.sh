#!/bin/bash

sshpass -f "/home/svc-jenkins/.cfgpass" scp -rp /tmp/teste svc-jenkins@wasd101:/tmp
