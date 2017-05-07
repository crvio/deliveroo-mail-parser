# deliveroo-mail-parser
A collection of scripts aimed at parsing information sent from deliveroo by mail to its riders

It uses python 3.5.0.
In case of incompatibilities with the version you are running I recommend taking a look into pyenv, which in my opinion comes very handy to manage python versions being run.

The get_deliveroo_mails.py script gets the email and saves the data in a json file.

The analyze_deliveries.py script analyzes the deliveries stored in the json file and displays useful information per date in a specified period of time.
More detailed information is available with the verbose flag (-v).

For usage information run the scripts with the help flag (-h).

