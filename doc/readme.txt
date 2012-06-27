== Installation ==
1. Instal the virtualenv
If you can not use the system virtualenv, please use the virtualenv.py in this directory.

2. Make a "scraper" directory and copy the code to this directory.
$ mkdir scraper
$ cd scraper

3. Build virtualenv
$ python virtualenv.py env
$ source env/bin/activate
(env) $ pip install -r doc/requirement.txt

4. Test
$ (env) python test.py
Should be print message like below:
    Ran 4 tests in 2.498s

    OK

5. Run
$ (env) python main.py path/input/csv_file.csv
Should be print message as below:
    [ #################################################################### ] 100%

    24 records has been saved to database data.db

The result will write to data.db (sqlite3)
Check if have error in log.txt

6. Run the webapp
$ (env) nohup python webapp &
It'll run the webapp on background. You can visit the webapp from http://65.60.12.130:8880/
If you want to stop the webapp, just use kill command to kill the process

7. Configure the cronjob
$ http://65.60.12.130:8880/settings