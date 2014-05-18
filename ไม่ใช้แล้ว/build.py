#-*-coding:utf8-*-
#!/usr/bin/python

import re, shutil, os, subprocess, traceback, glob
def genpaths (multils, projdir=""):
    suc=[]
    for l in multils:
        if type(l) == type([]):
            suc.extend(genpaths (l, projdir+multils[multils.index(l)-1]+"/"))
        else: 
            suc.append( projdir+l)
    return filter(None, suc)

def easylist (s):
    s=eval("['''"+re.sub("(\]+)(''',''')?", "'''\\1,'''",re.sub("(''',''')?(\[+)","''',\\2'''",re.sub(",","''','''",s)))+"''']")
    return s

def bashlist (s):
    s=eval("['''"+re.sub("(\}+)(''',''')?", "'''\\1,'''",re.sub("(/)?(\{+)","''',\\2'''",re.sub(",","''','''",s))).replace("{","[").replace("}","]")+"''']")
    return s

def pythonGenPath (s):
    return genpaths(easylist (s))

def bashGenPath (s):
    return genpaths(bashlist (s))
    
subprocess.call(["python", "-m", "compileall", "-f", "./winpath.py"])
appname="winpath-1.0a"
projdir="/home/%s/พื้นโต๊ะ/%s"%(os.getlogin(), appname)
if os.path.exists(projdir):
	shutil.rmtree(projdir)
dirBranch=pythonGenPath("etc,[udev,[rules.d]],usr,[bin,share,[applications,icons,winpath]],computer,DEBIAN")
appBranch=easylist(",,[winpath.rules],,[winpath],,winpath.desktop,winpath.png,[winpath.pyc,winpath.en.html,winpath.th.html,version],,")
for i in range(len(appBranch)):
    if not os.path.exists(projdir+"/"+dirBranch[i]):
	os.makedirs(projdir+"/"+dirBranch[i])
    if type(appBranch[i])==type([]):
	for j in appBranch[i]:
	    print j+" -> "+projdir+"/"+dirBranch[i]+"/"+j
	    shutil.copy2(j,projdir+"/"+dirBranch[i]+"/"+j)
    else:
	if appBranch[i]!="": 
	    shutil.copy2(appBranch[i],projdir+"/"+dirBranch[i])
print "Generating md5..."
os.remove(appname+".md5")
subprocess.check_output(["bash", "./md5sums.sh", projdir])
with open(appname+".md5") as f:
    d=f.read()
with open(appname+".md5", "w") as f:
    f.write(d.replace(projdir+"/",""))
print appname+".md5 -> DEBIAN/md5sums"
shutil.copy(appname+".md5",projdir+"/DEBIAN/md5sums")
print "Go to -> "+projdir
os.chdir(projdir)
size=subprocess.check_output(["du", "-ac", "--apparent-size", "--block-size=1024", projdir]).strip().split("\n")[-1].split("	")[0]
print "Totle Size: "+size
print "Generating control file..."
with open("DEBIAN/control", "w") as f:
	f.write("""Package: winpath
Version:0.1.0
Section: accessories
Priority: optional
Architecture: all
Depends: python (>=2.5), udisks, hwinfo, mount, nautilus, oxygen-icon-theme
Installed-Size: %s
Maintainer: UhBaUnTaUh
Description: Generator of windows style computer scheme path
"""%(size))# Must end with 1 blank line
for root, dirs, files in os.walk(projdir):
    for basename in files:
	z = os.path.join(root, basename)
	print "chmod ... "+z
	os.chmod(z, 0755)
os.chmod(projdir+"/computer", 0777)
print 
os.chdir("..")
print subprocess.check_output(["fakeroot", "dpkg", "--build", appname, appname+".deb"])
print "success!!!"
