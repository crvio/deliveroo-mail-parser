# deliveroo-mail-parser
A collection of scripts aimed at parsing information sent from deliveroo by mail to its riders

It uses python 3.5.0.
In case of incompatibilities with the version you are running I recommend taking a look into [pyenv](https://github.com/pyenv/pyenv), which in my opinion comes very handy to manage python versions being run.

I used the [Gmail Python Quickstart API](https://developers.google.com/gmail/api/quickstart/python). There's the necessary information to install it and to get the script running with the needed authorization.

The `get_deliveroo_mails.py` script gets the email and saves the data in a json file.

The `analyze_deliveries.py` script analyzes the deliveries stored in the json file and displays useful information per date in a specified period of time.
More detailed information is available with the verbose flag (-v).

In order for the scripts to work you need to have your deliveroo delivery mails labeled somehow. There's a file with the filter I use. If you have any other filter which successfully does so, it should also work, provided you give the label name with the `--label` option of `get_deliveroo_mails.py`.

For usage information run the scripts with the help flag (-h).

