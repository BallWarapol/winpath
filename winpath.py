#!/usr/bin/python
#-*-coding:utf8-*-
import os
import glob
import subprocess
import traceback
import time
import shutil
import re
from collections import namedtuple
from operator import itemgetter

devMode=False

def disk_usage(path):
	"""Return disk usage statistics about the given path.
	Returned valus is a named tuple with attributes 'total', 'used' and
	'free', which are the amount of total, used and free space, in bytes.
	"""
	st = os.statvfs(path)
	free = st.f_bavail * st.f_frsize
	total = st.f_blocks * st.f_frsize
	used = (st.f_blocks - st.f_bfree) * st.f_frsize
	return [total, used, free]

def gig(byteL):
	for i in range(len(byteL)):
		byteL[i]=byteL[i]/1024/1024/1024
	return byteL
	
icons=["",
	"/usr/share/icons/oxygen/48x48/devices/drive-removable-media-usb.png",#1.usb-disk
	"/usr/share/icons/oxygen/48x48/devices/drive-optical.png",#locked-disk
	"/usr/share/icons/oxygen/48x48/places/folder-locked.png",
	"/usr/share/icons/oxygen/48x48/devices/computer.png",
	"/usr/share/icons/oxygen/48x48/status/dialog-password.png",#5
	"/usr/share/icons/oxygen/48x48/devices/media-optical.png",#cd
	"/usr/share/icons/oxygen/48x48/devices/drive-harddisk.png",#hdd
	"/usr/share/icons/winpath.png",
	"/usr/share/icons/oxygen/48x48/places/user-home.png"#9
	]
def setDirIcon (path, iconNum):
	if os.path.exists(icons[iconNum]):
		subprocess.call(["gvfs-set-attribute", path, "metadata::custom-icon", "file://"+icons[iconNum]])

def desktopFormatGenerator(name, path, icon="folder", l=[""],exe="xdg-open"):
	l="\n".join(l)
	return """[Desktop Entry]
Name=%s
Exec=%s "%s"
Icon=%s
Terminal=false
StartupNotify=true
Type=Application
Categories=Application;Accessories;
%s
"""%(name, exe, path, icon, l)

def launcherCreater(name, path, dest, icon="", l=[""], exe="xdg-open"):
	if os.path.exists(dest):
		os.remove(dest)
	d=desktopFormatGenerator(name, path, icon, l, exe)
	dest=dest+".desktop"
	with open(dest, "w") as f:
		f.write(d)
	os.chmod (dest, 0777)
		
def getDriveInfo ():
	"""
lsblk -l format:
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
sda      8:0    0 149.1G  0 disk 
├─sda1   8:1    0   4.9G  0 part 

	df command Format:
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda6        15G  5.7G  8.3G  41% /
none            4.1k     0  4.1k   0% /sys/fs/cgroup
	old
	0.'/dev/sdc5', 
	1.'/media/v2ntfs416g', 
	2.'fuseblk', 
	3.'(rw,nosuid,nodev,allow_other,blksize=4096,default_permissions)', 
	4.'v2ntfs416g', 
	5.'/dev/scd1, /dev/disk/by-id/usb-HUAWEI_Mass_Storage-0:0, /dev/disk/by-path/pci-0000:00:1a.1-usb-0:2:1.2-scsi-0:0:0:0, /dev/cdrom1', 
	6.'fileSys0'"""
	lsblkcmd=[]
	ls=subprocess.check_output(["lsblk", "-l"]).strip().split("\n")
	mnts=subprocess.check_output(["mount", "-l"])
	for l in ls:
		if l[0:4] == "NAME":
			continue
		try:
			l=re.split(" *", l)
			l[0]="/dev/"+l[0]
			lsblkcmd.append(l) 
			subprocess.call(["udisks","--mount", l[0]])
		except Exception, err:
			traceback.print_exc()
	drives=[]
	for l in mnts.split("\n"):
		if l[0:5]=="/dev/":
			l=l.split(" on ",1)
			z=l[1].split(" type ",1)
			z=[z[0]]+z[1].split(" ",2)
			l=[l[0]]+z
			try:
				l[4]=l[4].strip().lstrip("[").rstrip("]")
			except:
				l.append("")
			l[2]=l[2].lower()
			for z in lsblkcmd:
				if l[0]==z[0]:
					if l[2].find("iso")>-1:
						z.append("fileSys4")
					elif l[2].find("ext")>-1:
						z.append("fileSys3")
					elif l[2].find("fat")>-1:
						z.append("fileSys2")
						l[2]="fat"                       
					elif l[2].find("fuseblk")>-1 :
						z.append("fileSys1")
						l[2]="ntfs"
					else:
						z.append("fileSys4")
					drives.append(l+z[1:])
	return drives
	
def mkSymlink (src, ln, icoNum=-1):
	if os.path.exists(ln):
		os.remove(ln)
	try:
		os.symlink(src, ln)
		os.chmod (ln, 0755)
	except:
		"print Error: mkSymlink (src, ln, icoNum=-1)"
	if icoNum!=-1:
		setDirIcon(ln, icoNum)
		
appFileName=os.path.basename(__file__)
rootPath="/opt/winpath"
configPath=rootPath+"/c/"+appFileName.rsplit(".",1)[0]
beautifulPath=configPath+"/beatiful-view/computer"
easyAccessPath=configPath+"/easyaccess-view/computer"
computerShortcutPath=configPath+"/computerShortcut"
cPath=rootPath+"/c"
windowsPath=cPath+"/windows"
fontsPath=windowsPath+"/fonts"
programsPath=cPath+"/programs"
usersPath=cPath+"/users"
winePath=configPath+"/c-wine"
lastDrives=[]

if 1==1:
	#clear every links, for freshy links.
	for l in glob.glob(rootPath+"/*"): 
		try:
			shutil.rmtree(l)
		except:
			os.remove(l)
	#no need activation dirs
	for z in [configPath,beautifulPath,easyAccessPath,computerShortcutPath, windowsPath, fontsPath, programsPath, usersPath, winePath]:
		if not os.path.exists(z):
			os.makedirs(z)
			os.chmod (z, 0777)
	setDirIcon(rootPath, 4)
	setDirIcon(cPath, 7)
	setDirIcon(easyAccessPath, 4)
	setDirIcon(beautifulPath, 4)
	setDirIcon(configPath, 8)
	#c
	z="C) ไดร์ฟ C ของ Windows - Wine - Linux"
	mkSymlink(rootPath+"/c", easyAccessPath+"/"+z, 7)
	launcherCreater(z, rootPath+"/c", beautifulPath+"/"+z, icons[7], ["Name[th]="+z])
	#windows
	launcherCreater("/", "/", windowsPath+"/root-access", icons[5], ["Name[th]=/"], "gksudo xdg-open")
	launcherCreater("system-fonts", "/usr/share/fonts", fontsPath+"/system-fonts", icons[5], ["Name[th]=system-fonts"], "gksudo xdg-open")
	#mkSymlink("/", windowsPath+"/root")
	#launcherCreater("Root Administrator", windowsPath+"/root", windowsPath+"/root-access", icons[5], ["Name[th]=คลิก! เพื่อแก้ไขไฟล์ใน root"], "gksudo nautilus")
	#programs
	y="วิธีติดตั้งและสำรองโปรแกรมในลินุกส์"
	with open("%s/%s.html"%(programsPath,y),"w") as z:
		z.write("""<html><head><meta charset="UTF-8" /><title>%s</title></head>
		<body><b>การติดตั้ง</b></br>ใช้โปรแกรม Software Center หรือ  Synaptic ในการติดตั้ง
		</br>โปรแกรมพวกนี้ใช้งานเหมือน Play Store หรือ คลังโปรแกรมของ 
		</br>Android บนมือถือนั่นเอง. ไม่นิยมโหลดจากที่อื่น เพราะเสี่ยงติดไวรัส
		</br></br><b>การแบ็คอัพ home และโปรแกรมต่างๆ</b>
		</br>การตั้งค่าโปรแกรมจะอยู่ในโฟลเดอร์ home 
		</br>ผู้ใช้ลินุกส์จึงนิยมแยกโฟลเดอร์ / กับ /home 
		</br>ออกเป็นคนละพาร์ทิชั่น เพราะเมื่อต้องการติดตั้ง หรือ 
		</br>อัพเกรด OS รุ่นใหม่ๆ การตั้งค่าโปรแกรม 
		</br>และไฟล์ทุกอย่างใน home จะยังคงอยู่เหมือนเดิม
		</br></br>การสำรองโปรแกรมไม่นิยมทำใน linux
		</br>เพราะโปรแกรมที่ให้มากับ OS มักมีเพียงพอต่อการใช้งานอยู่แล้ว
		</br>และโปรแกรมอื่นๆ ก็มีในคลังซอฟแวร์อยู่แล้วเช่นกัน
		</br>การเก็บโปรแกรมเก่าๆ ไว้ จึงไม่มีประโยชน์
		</br>เสียพื้นที่ดิสก์, เสียเวลา, และอาจทำให้เครื่องรวนได้
		</br></br>สำหรับท่านที่ไม่ได้แยก home แต่แรก และท่านที่
		</br>ต้องการเก็บรายชื่อโปรแกรมไว้ใช้ข้ามรุ่น สามารถศึกษาได้ที่:
		</br><a href="http://askubuntu.com/questions/9135/best-way-to-backup-all-settings-list-of-installed-packages-tweaks-etc">Best way to backup all settings, list of installed packages, tweaks, etc?</a>
		"""%y)
	#launcherCreater("usr", "/usr", programsPath+"/usr-access", icons[5], ["Name[th]=usr"], "gksudo xdg-open")
	#mkSymlink("/usr", programsPath+"/usr")
	#launcherCreater("Usr Administrator", programsPath+"/usr", programsPath+"/usr-access", icons[5], ["Name[th]=คลิก! เพื่อแก้ไขไฟล์ใน usr"], "gksudo nautilus")
	#home
	home="/home/"+os.getlogin()
	mkSymlink(home, rootPath+"/c/users/home")
	#wine
	launcherCreater("C: of wine", winePath, cPath+"/c-of-wine", icons[7], ["Name[th]=C: ของโปรแกรม wine"])
	#desktop icons
	launcherCreater("Computer       Beautiful", beautifulPath, computerShortcutPath+"/beautiful", "computer", ["Name[th]=คอมพิวเตอร์        ลิงก์หน้าต่างใหม่"])
	launcherCreater("Computer       Easy to Access", easyAccessPath, computerShortcutPath+"/easy-access", "computer", ["Name[th]=คอมพิวเตอร์        เข้าถึงง่าย"])
	launcherCreater("Computer       Direct Access", rootPath, computerShortcutPath+"/direct-access", "computer", ["Name[th]=คอมพิวเตอร์     เข้าถึงโดยตรง"])
	launcherCreater("winPath", computerShortcutPath, configPath+"/winpath", icons[8], ["Name[th]=วินพาธ:winPath", "Comment=winPath: Windows path on linux", "Comment[th]=ระบบไฟล์แบบวินโดวส์บนระบบลินุกส์"])
	mkSymlink(computerShortcutPath+"/easy-access.desktop", beautifulPath+"/easy-access.desktop")
	mkSymlink(computerShortcutPath+"/beautiful.desktop", easyAccessPath+"/beautiful.desktop")

winDrive=""
for l in getDriveInfo():
		if (l[2]=="ntfs" or l[2]=="fat") and subprocess.check_output(["ls", l[1]]).find("Program Files")>-1:
			launcherCreater("C: of old windows", l[1], rootPath+"/c/c-of-old-windows-link", icons[7], ["Name[th]=ไดร์ฟ C: วินโดวส์เดิม"])
			winDrive=l
			break

home="/home/"+os.getlogin()
z="c-wine-of-"+os.getlogin()
if not os.path.exists(winePath+"/"+z):
	wine=home+"/.wine"
	if not os.path.exists(wine): os.makedirs(wine)
	launcherCreater("C: of user '%s'"%os.getlogin(), wine, winePath+"/"+z, "folder", ["Name[th]=C: ของผู้ใช้ '%s'"%os.getlogin()])

z="fonts-of-"+os.getlogin()
if not os.path.exists(fontsPath+"/"+z):
	zz=home+"/.local/share/fonts"
	if not os.path.exists(zz): os.makedirs(zz)
	launcherCreater("Fonts of user '%s'"%os.getlogin(), zz, fontsPath+"/"+z, "folder", ["Name[th]=โฟลเดอร์ Fonts ของผู้ใช้ '%s'"%os.getlogin()])
	#make link per user
	mkSymlink(computerShortcutPath+"/easy-access.desktop", home+"/easy-access.desktop")
	mkSymlink(configPath+"/winpath.desktop", home+"/.local/share/applications/winpath.desktop")
	
	z="/.gtk-bookmarks"
	zz=subprocess.check_output(["lsb_release","-is"])
	if zz >= "13.04":
		z="/.config/gtk-3.0/bookmarks"
	with open(home+z) as f:
		d=f.read()
	if d.find(easyAccessPath)==-1:
		with open(home+z+".bk", "w") as fw:
			fw.write(d)
		with open(home+z, "w") as fw:
			fw.write("file://"+easyAccessPath+"\n"+d)

#start	
def curDisks():
	return subprocess.check_output(["ls", "-l", "/dev/disk/by-id"])
lastDisks=""
while 1==1:	
	if lastDisks!=curDisks():
		lastDisks=curDisks()
		drives=getDriveInfo()
		drives=sorted(drives, key=itemgetter(len(drives[0])-1,0))
		try:
			for l in lastDrives:
				if not l[0:-1] in drives:
					for p in l[-1]:
						if os.path.exists(p):
							os.remove(p)
					lastDrives.remove(l)
		except Exception, err:
			traceback.print_exc()
		c=99
		for l in drives:
			if l in [z[:-1] for z in lastDrives]:
				continue
			c+=1
			try:
				if l[0]==winDrive[0]:
					c-=1
					continue
			except Exception, err:
				traceback.print_exc()    
			driveLabel="Local Disk"
			driveIcon=7
			if l[6]=="1" :
				 driveLabel="Removeable Disk"
				 driveIcon=1
			elif l[2].find("iso")>-1:
				 driveLabel="CD-DVD Drive"
				 driveIcon=6
				 for z in os.listdir(l[1]):
					if re.search(".ico", z):
						icons.append(l[1]+"/"+z)
						driveIcon=len(icons)-1
			elif l[1]=="/home":
				driveLabel="linux-users-drive(home)"
				driveIcon=9           
			elif l[1]=="/":
				driveLabel="linux-windows-folder(root)"
				driveIcon=7
			if l[4]!="": 
				driveLabel=l[4]
			linkTarget="%s/%s"%(rootPath,chr(c))
			z=gig(disk_usage(l[1]))
			sortedByDrive="%s) %s - %s G free of %s G - %s"%(chr(c).upper(),driveLabel,z[2],z[0],l[2].upper())
			sortedByLabel="%s (%s:) - %s G free of %s G - %s Filesystem"%(driveLabel,chr(c).upper(),z[2],z[0],l[2].upper())
			if not l in [z[0:-1] for z in lastDrives] :
				mkSymlink(l[1], linkTarget, driveIcon)
				e=easyAccessPath+"/"+sortedByDrive
				mkSymlink(l[1], e, driveIcon)
				b=beautifulPath+"/"+sortedByDrive
				launcherCreater(sortedByLabel, linkTarget, b, icons[driveIcon], ["Name[th]="+sortedByDrive])
				l.append([linkTarget,e,b])
				lastDrives.append(l)
	time.sleep(15)
					
