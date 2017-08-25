# -*- coding: utf-8 -*-
from LineAlpha import LineClient
from LineAlpha.LineApi import LineTracer
from LineAlpha.LineThrift.ttypes import Message
from LineAlpha.LineThrift.TalkService import Client
from datetime import datetime
import time, random ,sys, re, string, os, json, threading

reload(sys)
sys.setdefaultencoding('utf-8')

client = LineClient()
client._qrLogin("line://au/q/")
#_tokenLogin("EkBawCszC48fBlTU755b.bCOO/5H4f62FSyzyp+jJsW.Vej1q+b7abS8GpzeT9kDuIh6cJrnQMfPtjCRlsFdhL0=")

profile, setting, tracer = client.getProfile(), client.getSettings(), LineTracer(client)
offbot, messageReq, wordsArray, waitingAnswer = [], {}, {}, {}

print client._loginresult()

wait = {
    'readPoint':{},
    'readMember':{},
    'setTime':{},
    'ROM':{},
   }

setTime = {}
setTime = wait["setTime"]

def sendMessage(to, text, contentMetadata={}, contentType=0):
    mes = Message()
    mes.to, mes.from_ = to, profile.mid
    mes.text = text

    mes.contentType, mes.contentMetadata = contentType, contentMetadata
    if to not in messageReq:
        messageReq[to] = -1
    messageReq[to] += 1
    client._client.sendMessage(messageReq[to], mes)

def NOTIFIED_ADD_CONTACT(op):
    try:
        sendMessage(op.param1, client.getContact(op.param1).displayName + "Thanks for add")
    except Exception as e:
        print e
        print ("\n\nNOTIFIED_ADD_CONTACT\n\n")
        return

tracer.addOpInterrupt(5,NOTIFIED_ADD_CONTACT)

def NOTIFIED_INVITE_INTO_GROUP(op):
    try:
        if op.type == 13:
            client.acceptGroupInvitation(op.param1)
    except Exception as e:
        print e
        print ("\n\nNOTIFIED_INVITE_INTO_GROUP\n\n")
        return

tracer.addOpInterrupt(13,NOTIFIED_INVITE_INTO_GROUP)

def NOTIFIED_ACCEPT_GROUP_INVITATION(op):
    try:
        sendMessage(op.param1, "hi, " + client.getContact(op.param2).displayName)
        sendMessage(op.param1, text="gift sent", contentMetadata={"STKID": "247", "STKPKGID": "3", "STKVER": "100" }, contentType=7)
    except Exception as e:
        print e
        print ("\n\nNOTIFIED_ACCEPT_GROUP_INVITATION\n\n")
        return

tracer.addOpInterrupt(17,NOTIFIED_ACCEPT_GROUP_INVITATION)

def NOTIFIED_KICKOUT_FROM_GROUP(op):
    try:
        if op.type == 19:
            sendMessage(op.param1, "Wtf? " + client.getContact(op.param2).displayName)
            client.inviteIntoGroup(op.param1,[op.param3])
        #sendMessage(op.param1, client.getContact(op.param3).displayName + " Good Bye\n(*´･ω･*)")
    except Exception as e:
        print e
        print ("\n\nNOTIFIED_KICKOUT_FROM_GROUP\n\n")
        return

tracer.addOpInterrupt(19,NOTIFIED_KICKOUT_FROM_GROUP)

def NOTIFIED_LEAVE_GROUP(op):
    try:
        sendMessage(op.param1, "Good Bye " + client.getContact(op.param2).displayName + "\n  (*´･ω･*)")
        client.inviteIntoGroup(op.param1,[op.param2])
        #sendMessage(op.param1, text="gift sent", contentMetadata={"STKID": "9", "STKPKGID": "1", "STKVER": "100" },contentType=7 )
    except Exception as e:
        print e
        print ("\n\nNOTIFIED_LEAVE_GROUP\n\n")
        return

tracer.addOpInterrupt(15,NOTIFIED_LEAVE_GROUP)

def NOTIFIED_READ_MESSAGE(op):
    #print op
    try:
        if op.param1 in wait['readPoint']:
            Name = client.getContact(op.param2).displayName
            if Name in wait['readMember'][op.param1]:
                pass
            else:
                wait['readMember'][op.param1] += "\n・" + Name
                wait['ROM'][op.param1][op.param2] = "・" + Name
        else:
            pass
    except:
        pass

tracer.addOpInterrupt(55, NOTIFIED_READ_MESSAGE)

def RECEIVE_MESSAGE(op):
    msg = op.message
    try:
        if msg.contentType == 0:
            try:
                if msg.to in wait['readPoint']:
                    if msg.from_ in wait["ROM"][msg.to]:
                        del wait["ROM"][msg.to][msg.from_]
                else:
                    pass
            except:
                pass
        else:
            pass
    except KeyboardInterrupt:
	       sys.exit(0)
    except Exception as error:
        print error
        print ("\n\nRECEIVE_MESSAGE\n\n")
        return

tracer.addOpInterrupt(26, RECEIVE_MESSAGE)

def SEND_MESSAGE(op):
    msg = op.message
    try:
        if msg.toType == 0:
            if msg.contentType == 0:
                if msg.text == "Mid":
                    sendMessage(msg.to, msg.to)
                if msg.text == "Me":
                    sendMessage(msg.to, text=None, contentMetadata={'mid': msg.from_}, contentType=13)
                if msg.text == "Gift":
                    sendMessage(msg.to, text="gift sent", contentMetadata=None, contentType=9)
                else:
                    pass
            else:
                pass
        if msg.toType == 2:
            if msg.contentType == 0:
                if msg.text in ["Mid", "mid"]:
                    sendMessage(msg.to, msg.from_)
                if msg.text == "Gid":
                    sendMessage(msg.to, msg.to)
                if msg.text == "Ginfo":
                    group = client.getGroup(msg.to)
                    md = "Name: " + group.name + "\n\nId: " + group.id + "\n\nGroup Picture: http://dl.profile.line-cdn.net/" + group.pictureStatus
                    if group.preventJoinByTicket is False: 
                        md += "\n\nInvitationURL: " +  "line://ti/g/" + client._client.reissueGroupTicket(msg.to)
                    else: 
                        md += "\n\nInvitationURL: Refusing"
                    if group.invitee is None: 
                        md += "\n\nMembers: " + str(len(group.members)) + "\n\nInvited: -"
                    else: 
                        md += "\n\nMembers: " + str(len(group.members)) + "\n\nInvited: " + str(len(group.invitee))
                    sendMessage(msg.to,md)
                if "Gname: " in msg.text:
                    key = msg.text.replace("Gname: ","")
                    group = client.getGroup(msg.to)
                    group.name = key
                    client.updateGroup(group)
                    sendMessage(msg.to,"Group name canged to "+key)
                if msg.text == "Gurl":
                    sendMessage(msg.to,"line://ti/g/" + client._client.reissueGroupTicket(msg.to))
                if msg.text == "Gopen":
                    group = client.getGroup(msg.to)
                    if group.preventJoinByTicket == False:
                        sendMessage(msg.to, "Already Open")
                    else:
                        group.preventJoinByTicket = False
                        client.updateGroup(group)
                        sendMessage(msg.to, "Group URL Open")
                if msg.text == "Gclose":
                    group = client.getGroup(msg.to)
                    if group.preventJoinByTicket == True:
                        sendMessage(msg.to, "Already Close")
                    else:
                        group.preventJoinByTicket = True
                        client.updateGroup(group)
                        sendMessage(msg.to, "Group URL Close")
                if "Kick: " in msg.text:
                    key = msg.text.replace("Kick: ","")
                    group = client.getGroup(msg.to)
                    client.kickoutFromGroup(msg.to,[key])
                    contact = client.getContact(key)
                    sendMessage(msg.to, ""+contact.displayName+" sorry")
                if "Nk: " in msg.text:
                    key = msg.text[3:]
                    group = client.getGroup(msg.to)
                    Names = [contact.displayName for contact in group.members]
                    Mids = [contact.mid for contact in group.members]
                    if key in Names:
                        kazu = Names.index(key)
                        sendMessage(msg.to, "Bye")
                        client.kickoutFromGroup(msg.to, [""+Mids[kazu]+""])
                        contact = client.getContact(Mids[kazu])
                        sendMessage(msg.to, ""+contact.displayName+" Sorry")
                    else:
                        sendMessage(msg.to, "wtf dude??")
                if msg.text == "Cancel":
                    group = client.getGroup(msg.to)
                    if group.invitee is None:
                        sendMessage(op.message.to, "Nope")
                    else:
                        gInviMids = [contact.mid for contact in group.invitee]
                        client.cancelGroupInvitation(msg.to, gInviMids)
                        sendMessage(msg.to, str(len(group.invitee)) + " Done")
                if "Invite: " in msg.text:
                    key = msg.text[-33:]
                    client.findAndAddContactsByMid(key)
                    client.inviteIntoGroup(msg.to, [key])
                    contact = client.getContact(key)
                    sendMessage(msg.to, ""+contact.displayName+" I invited you")
                if msg.text in ["Good bye","good bye"]:
                    client.leaveGroup(msg.to)
                if msg.text in ["sp","Sp","Speed"]:
                    start = time.time()
                    elapsed_time = time.time() - start
                    sendMessage(msg.to, "%s Seconds" % (elapsed_time))
                if msg.text == "Me":
                    M = Message()
                    M.to = msg.to
                    M.contentType = 13
                    M.contentMetadata = {'mid': msg.from_}
                    client.sendMessage(M)
                if "Show: " in msg.text:
                    key = msg.text[-33:]
                    sendMessage(msg.to, text=None, contentMetadata={'mid': key}, contentType=13)
                    contact = client.getContact(key)
                    sendMessage(msg.to, ""+contact.displayName+"'s contact")
                if msg.text in ["Time","time"]:
                    sendMessage(msg.to, "Sekarang Jam " + datetime.datetime.today().strftime('%H:%M:%S\nTanggal  %Y-%m-%d '))
                if msg.text in ["Gift","gift"]:
                    sendMessage(msg.to, text="gift sent", contentMetadata=None, contentType=9)
                if msg.text in ["Set","set","?"]:
                    #sendMessage(msg.to, "􀜁􀅔Har Har􏿿")
                    try:
                        del wait['readPoint'][msg.to]
                        del wait['readMember'][msg.to]
                    except:
                        pass
                    wait['readPoint'][msg.to] = msg.id
                    wait['readMember'][msg.to] = ""
                    wait['setTime'][msg.to] = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    wait['ROM'][msg.to] = {}
                    print wait
                if msg.text in ["Cek","cek","!"]:
                    if msg.to in wait['readPoint']:
                        if wait["ROM"][msg.to].items() == []:
                            chiya = ""
                        else:
                            chiya = ""
                            for rom in wait["ROM"][msg.to].items():
                                print rom
                                chiya += rom[1] + "\n"

                        sendMessage(msg.to, "People who readed %s\nthat's it\n\nPeople who have ignored reads\n%sIt is abnormal ♪\n\nReading point creation date n time:\n[%s]"  % (wait['readMember'][msg.to],chiya,setTime[msg.to]))
                    else:
                        sendMessage(msg.to, "Nope")
                else:
                    pass
        else:
            pass

    except Exception as e:
        print e
        print ("\n\nSEND_MESSAGE\n\n")
        return

tracer.addOpInterrupt(25,SEND_MESSAGE)

while True:
    tracer.execute()
