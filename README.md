# pyslack

A command line python base interface to Slack. It uses Slack New App API verion 2.0.

## Install

Create an App on slack and enable `chat:write`, `im:write` and `files:write` permissions.
Install the app, and save the Bot User Token OAuth Access Token to `$HOME/.pyslackrc` from the template `pyslackrc.sample`. 
And install the python package.


``` bash
python -m pip install -r requirements.txt
python setup.py build && python setup.py install

```

**or**

``` bash
pip install .

```

## Usage

* Send a text message.

  ``` bash
  pyslack text --channel '#random' --text "This is a test message."
  ```

* Upload a file.

  ``` bash
  pyslack file --channel '#random' --file /path/to/file --title FileTitle --filetype <file type> \
    --initial-comment "This is the comment"
  ```
