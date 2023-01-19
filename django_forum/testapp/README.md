
To set up the test environment run the script `setup.sh`.  You must have podman installed, and ansible in a venv prefix.  This will install a set of containers inside a pod that are necessary to test the site.  Inside the script ansible calls ansible_setup_test.yml.  You can configure parameters in the yaml such as screen size for the selenium grid container, or memory usage per container.

To run the tests run the script `tests.sh`.  You can append one of the following constants to set the appropriate selenium variables. 
I locate these commands in a file - `bashrc.d/EXPORT` so that they are available in my terminal session.

export GUI="--gui --server=127.0.0.1 --port=4444 --browser=firefox"
export DEMO="--gui --demo --server=127.0.0.1 --port=4444 --browser=firefox"
export HLESS="--headless2 --disable-gpu --slow --demo-sleep=0.2"

Note* the default, with no options, is for pytest to run headless with `--headless2`.  The $HLESS option slows down the headless run in case of tests failing due to being run on too fast a processor.

You can add other commands after the constant, so for example `./tests.sh $HLESS -m pytest_example_mark`.  Later commands overwrite earliers commands.

The install includes a selenium container running selenium grid.   You can visit the novnc interface to the selenium container at the following address:

http://localhost:7900/?autoconnect=1&resize=scale&password=secret

If you want to run the server to view the site, then use `./runserver.sh`.

You can run the command `ansible-playbook ansible_teardown_test.yml` to clean up after running tests.

The test suite uses a podman pod of containers.  If there is an error, try running the command `podman pod stop django_forum_test_pod` and then `podman pod start django_forum_test_pod`.