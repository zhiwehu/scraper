== Installation ==
1. Instal the virtualenv
TBD

2. Make a "scraper" directory and copy the code to this directory.
$ mkdir scraper
$ cd scraper

3. Build virtualenv
$ virtualenv env
$ source env/bin/activate
$ (env) pip install -r doc/requirement.txt

4. Test
$ (env) python test.py
Should be print message like below:
    Ran 4 tests in 2.498s

    OK

5. Run
$ (env) python main.py path/input/csv_file.csv
Should be