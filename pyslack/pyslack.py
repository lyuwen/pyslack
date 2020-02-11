import os
import sys
import slack
import textwrap
import configparser
import argparse


CONFIG=os.path.join(os.environ['HOME'],'.pyslackrc')


class pySlack(object):
  ''' A python interface to slack
  '''
  def __init__(self, configfile=None):
    self.config = configparser.ConfigParser()
    if configfile is not None:
      self.config.read(configfile)
    else:
      self.config.read(CONFIG)
    self.BOT_USER_API_TOKEN = self.config.get('Slack', 'bot_user_api_token')
    self.client = slack.WebClient(token=self.BOT_USER_API_TOKEN)


  def postMessage(self, channel, text):
    '''
      Available flags
      token, text, channel, as_user, username, icon_emoji
    '''
    response = self.client.chat_postMessage(
        channel=channel, 
        text=text,
        ) 
    if not response['ok']:
      raise RuntimeError('Post message failed')


  def uploadFile(self, channel, file, filename=None, title=None, initial_comment=None, filetype=None):
    '''
      Available flags
      token, file, content, filetype, filename, title, initial_comment, channels
    '''
    response = self.client.files_upload(
        channels=channel,
        file=file,
        title=title if title is not None else '',
        initial_comment=initial_comment if initial_comment is not None else '',
        filename=filename if filename is not None else '',
        filetype=filetype if filetype is not None else '',
        )
    if not response['ok']:
      raise RuntimeError('File upload failed')


def main():
  parser = argparse.ArgumentParser(
      description='Post message or upload file to Slack via command line.',
      formatter_class=argparse.RawDescriptionHelpFormatter,
      epilog=textwrap.dedent('''
      Setting up .pyslackrc file:

        $ cat ~/.pyslackrc
        [Slack]
        bot_user_api_token=TOKEN1  #Required
      '''))
  subparsers = parser.add_subparsers()

  parser_text = subparsers.add_parser('text', help='Post a text message to Slack.')
  parser_text.add_argument('-c', '--channel', required=True, type=str, help='Channel to post message or upload file to.')
  parser_text.add_argument('-t', '--text', required=True, type=str, help='Text message to post.')
  parser_text.set_defaults(subparser='text')

  parser_file = subparsers.add_parser('file', help='Upload a file to Slack.')
  parser_file.add_argument('-c', '--channel', required=True, type=str, help='Channel to post message or upload file to.')
  parser_file.add_argument('-f', '--file', required=True, type=str, help='File to upload.')
  parser_file.add_argument('-t', '--title', type=str, help='Title of the file upload message.')
  parser_file.add_argument('-i', '--initial-comment', type=str, help='Initial comment to the file.')
  parser_file.add_argument('-y', '--filetype', type=str, help='Type of the file.')
  parser_file.set_defaults(subparser='file')

  args = parser.parse_args()

  pyslack = pySlack()

  if not hasattr(args, "subparser"):
    print("Please choose a mode between text and file.")
    print()
    parser.print_help()
    return 1

  if not (args.channel.startswith("#") or args.channel.startswith("@")):
    print("Channel name must start with either # or @")
    return 1

  if args.subparser == 'file':
    print('Uploading file...')
    pyslack.uploadFile(
        channel=args.channel, 
        file=args.file,
        filename=args.file,
        title=args.title,
        initial_comment=args.initial_comment,
        filetype=args.filetype
        )
    print('Done')
  elif args.subparser == 'text':
    print('Posting message...')
    pyslack.postMessage(
        channel=args.channel, 
        text=args.text,
        )
    print('Done')

  return 0


if __name__=='__main__':
  retval = main()
  sys.exit(retval)
