
To set up the test environment run `ansible-playbook ansible_setup_test.yml`  You must have podman installed, and obviously ansible in a venv prefix.  This will install a set of containers inside a pod that are necessary to test the site.

To run the tests run the script `tests.sh`.  You can append one of the following constants to set the appropriate selenium variables. 
I locate these commands in a file - `bashrc.d/EXPORT` so that they are available in my terminal session.

export GUI="--gui --server=127.0.0.1 --port=4444 --browser=firefox"
export DEMO="--gui --demo --server=127.0.0.1 --port=4444 --browser=firefox"
export HLESS="--headless2 --disable-gpu --slow --demo-sleep=0.2"

Note* the default is for pytest to run headless with `--headless2`.  The $HLESS option slows down the headless run in case of tests failing due to being run on too fast a processor.

You can add other commands after the constant, so for example `./tests.sh $HLESS -m pytest_example_mark`.  Later commands overwrite earliers commands.

If you want to run the server to view the site, then use `./runserver.sh`.