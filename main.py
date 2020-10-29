import subprocess
import argparse


EPILOG = __doc__
VALID_ENVS = {
    'fourfront': 'deploy_tests/fourfront/fourfront.py',
    'cgap': 'deploy_tests/cgap/cgap.py',
}


def main():
    parser = argparse.ArgumentParser(description='post-deploy-perf-tests entry point', epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('app', help='which application to test - one of "fourfront" or "cgap"')
    parser.add_argument('--headless', help='Whether or not to run in headless mode with default configuration',
                        action='store_true', default=False)
    args = parser.parse_args()
    app_lower = args.app.lower()

    if app_lower not in VALID_ENVS:
        raise RuntimeError('Gave invalid env %s, expected one of %s' % (app_lower, VALID_ENVS))

    locust_file_location = VALID_ENVS[app_lower]
    if not locust_file_location:
        raise RuntimeError('Tried to run tests on environment %s that has no configuration!' % app_lower)

    if args.headless:
        try:
            subprocess.call([
                'locust', '-f', locust_file_location,
                '--headless',
                '-u', '50',  # number of users
                '-r', '10',  # hatch rate
                '--run-time', '120s',
                '--print-stats'
            ])
        except KeyboardInterrupt:
            pass
    else:
        try:
            subprocess.call([
                'locust', '-f', locust_file_location
            ])
        except KeyboardInterrupt:
            pass
    exit(0)


if __name__ == '__main__':
    main()
