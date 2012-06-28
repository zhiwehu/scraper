== Installation ==
1. Install the virtualenv
   If you do not want to install virtualenv, it is also possible to use virtualenv.py in this directory.

2. Make a "scraper" directory and copy all of code to this directory.
$ mkdir scraper
$ cd scraper

3. Build virtualenv
$ python virtualenv.py env
$ source env/bin/activate
(env) $ pip install -r doc/requirement.txt

4. Test
$ (env) python tests.py
Should be print message like below:
    Ran 4 tests in 2.498s

    OK

5. Run
$ (env) python main.py data/good_format.csv
Should be print message as below:
    [ #################################################################### ] 100%

    24 records has been saved to database data.db

The result will write to data.db (sqlite3). Detailed debug and log information can be found in log.txt.

6. Run the webapp server
$ (env) nohup python webapp.py &
It'll run the webapp on background. You can visit the webapp from http://127.0.0.1:8880/
If you want to stop the webapp, just use kill command to kill the process.

7. Configure the cronjob
$ http://65.60.12.130:8880/settings