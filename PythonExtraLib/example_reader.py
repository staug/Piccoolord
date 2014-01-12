# -*- coding: utf-8 -*-
# attention, sous python2.x il sera peut-être nécessaire d'encoder les chaines de caractères
from pygame import *

from PythonExtraLib.reader import Reader

scr = display.set_mode((500,500))

message = """Ceci est le message à afficher, il sera automatiquement wrappé ...

pensez à encoder vos strings sous python2.x ...

(appuyez sur ESPACE pour continuer)"""

texte = Reader(message,pos=(10,10),width=200,font="Andale-mono.ttf", fontsize=16,height=300,bg=(200,200,200),fgcolor=(20,20,20))
texte.show()
while True:
    ev = event.wait()
    if ev.type == KEYDOWN and ev.key==K_SPACE: break

texte.ADD_TEXT = "il suffit d'affecter le @property TEXT pour changer le texte ..."
texte.show()
while True:
    ev = event.wait()
    if ev.type == KEYDOWN and ev.key==K_SPACE: break

texte.ADD_TEXT = "et d'actualiser avec la methode show()"
texte.show()
while True:
    ev = event.wait()
    if ev.type == KEYDOWN and ev.key==K_SPACE: break
    if texte.update(ev): texte.show()

texte.TEXT = "il y a plein d'autres possibilités, comme changer le background et le foreground"
texte.BG = 100,20,20
texte.FGCOLOR = 180,180,180
texte.show()
while True:
    ev = event.wait()
    if ev.type == KEYDOWN and ev.key==K_SPACE: break

display.update(scr.fill(0,texte)) #efface la frame car les dimensions vont changer
texte.size = 250,150 #nouvelles dimensions
texte.TEXT = """utilez la molette pour faire défiler
ctrl+ et ctrl- pour modifier la taille du texte


on peut aussi scroller, increase et decrease le texte, (selectionner du texte ne sert pas pour le moment) ...

mais celà nécessite d'utiliser une boucle événementielle.

n'hésitez pas à me demander pour plus d'info ;)"""
texte.BG = 100,20,20
texte.FGCOLOR = 180,180,180
texte.show()
while True:
    ev = event.wait()
    if ev.type == KEYDOWN and ev.key==K_SPACE: break
    if texte.update(ev): texte.show()