#!/usr/bin/python
#-*-coding:utf8-*-
import os
import subprocess
import traceback
    
hwinfo=[]
for z in subprocess.check_output(["hwinfo", "--cdrom", "--partition"]).split("Device Files: "):
    try:
        z=z.split("\n")[0].split(", ")
        hwinfo.append(z[0:3]+["|".join(z[3:])]) 
        try:
            os.system("udisks --mount '%s'"%z[5])
        except:
            os.system("udisks --mount '%s'"%z[0])
    except Exception, err:
        traceback.print_exc()
