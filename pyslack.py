#!/usr/bin/env python
import sys, os, json
import requests
import configparser
from inputs import inputs
CONFIG=os.path.join(os.environ['HOME'],'.pyslackrc')
''' This is almost same as vim-slack setting
$ cat .pyslackrc
[Slack]
slack_fileupload_token=TOKEN1
slack_incoming_token=TOKEN2
'''

class pySlack(object):
  def __init__(self):
    self.config = configparser.ConfigParser()
    self.config.read(CONFIG)
    for n,v in self.config.items('Slack'):
      exec("self.%s='%s'"%(n,v))
    if dir(self).count('slack_fileupload_token')==0:
      print 'Missing slack_fileupload_token'
      sys.exit()
    if dir(self).count('slack_incoming_token')==0:
      print 'Missing slack_incoming_token'
      sys.exit()

  def get_channel_ids(self):
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    respond=requests.post("https://slack.com/api/channels.list",headers=headers, data={u'token':self.slack_fileupload_token})
    all_channels=dict(('#'+s['name'],s['id']) for s in respond.json()['channels'] if s["is_member"]==True)
    respond=requests.post("https://slack.com/api/users.list",headers=headers, data={u'token':self.slack_fileupload_token})
    member_channels=dict((s['name'], s['id']) for s in respond.json()['members'])
    for n,i in member_channels.items(): all_channels['@'+n]=i
    self.channels=all_channels


  def post(self, **kwargs):
    '''
      Available flags
      text, username, channel, icon_emoji
    '''
    payload={
        'text': '',
        'channel': '#general',
        'username': 'pyslack-bot',
        'icon_emoji': ':ghost:',
        }
    payload.update(kwargs)
    headers = {'content-type': 'application/json'}
    respond=requests.post(self.slack_incoming_token,headers=headers, data=json.dumps(payload))
    print respond.text

  def uploadFile(self, **kwargs):
    '''
      Available flags
      token, file, content, filetype, filename, title, initial_comment, channels
    '''
    payload={
        #'channels': '#general',
        'filetype': 'auto',
        }
    payload.update(kwargs)
    
    url='https://slack.com/api/files.upload'
    #print payload.keys().count('file')+payload.keys().count('content')
    if payload.keys().count('file')+payload.keys().count('content')!=1:
      print "You must provide either a file or content parameter."
      sys.exit()
    if payload.keys().count('file'):
      if payload.keys().count('filename')==0:payload['filename']=payload['file']
      if payload.keys().count('title')==0:payload['title']=payload['file']
    payload['token']=self.slack_fileupload_token
    options=[]
    for s in payload.keys():
      if s=='file':
        options.append('-F %s=@%s'%(s,payload[s]))
      elif s=='content':
        options.append('-F %s="%s"'%(s,payload[s]))
      else:
        options.append('-F %s="%s"'%(s,payload[s]))
    cmd='curl '+' '.join(options)+' '+url+" 2>/dev/null"
    #print cmd
    message=os.popen(cmd).read()
    print "Done"

if __name__=="__main__":
  av=inputs("""
      text=str channel=str username=str icon_emoji=str filetype='auto' initial_comment=str title=str file=str
      I=str y=str
  """)
  av.update(sys.argv[1:])
  pyslack=pySlack()
  pyslack.get_channel_ids()
  #pyslack.post(text='Hello world!')
  if av.count("channel"):
    if av.count('file'):
      print "file mode"
      channel_id=pyslack.channels[av.channel]
      if os.path.exists(av.file):
        if av.count('I'):
          # Interactively gather information
          payload={'file':av.file, 'channels':channel_id, 'channel_name':av.channel}
          if not av.count('title'):
            payload['title']=raw_input("Title: ")
          if not av.count('initial_comment') and raw_input( "Add initial comment?[yN]: ").lower() in ['y','yes']:
            payload['initial_comment']=raw_input("Initial Comment: ")
          # Print confirmation
          print 10*"="+"Post information"+10*"="
          print "File: ", payload['file']
          print "Channel: ", payload['channel_name']
          print "Title: ", payload['title']
          if payload.keys().count('initial_comment'): print "Initial comment: ", payload['initial_comment']
          print 36*"="
          if raw_input( "Post?[yN]: ".format(av.file,av.channel)).lower() in ['y','yes']:
            pyslack.uploadFile(**payload)
        elif av.count('y') or raw_input( "Upload {} to channel {}, proceed?[yN]: ".format(av.file,av.channel)).lower() in ['y','yes']:
          print "uploading"
          pyslack.uploadFile(file=av.file,channels=channel_id,**dict((s,av.get_dict()[s]) for s in "filetype filename title initial_comment".split() if av.count(s)))
        else:
          print "Abort"
      else:
        raise AttributeError("File not exists!")
    elif av.count('text'):
      print "posting mode"
      if av.count('y') or raw_input( "Post \"{}\" to channel {}, proceed?[yN]: ".format(av.text,av.channel)).lower() in ['y','yes']: 
        print "posting"
        pyslack.post(**av.get_dict())
      else:
        print "Abort"
    else:
      raise AttributeError("Missing attribute file or text!")
  else:
    raise AttributeError("Missing attribute channel!")
  #pyslack.uploadFile(file="pyslack.py")
