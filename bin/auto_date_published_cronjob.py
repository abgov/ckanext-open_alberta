# this program is used to call organization api
# to renew all the datasets in the dataase whose published
# date is bofore or the same day of the current day and also
# the dataset's private field is true (private state). The 
# result is that all the datasets with the above state will
# be flipped to public state(private field is false). 
# This task should be implemented once every day with system
# admin authorization by cronjob. Do not run this program 
# frequently in one day. It will take too much time to run 
# the database record checking. 

import json
import os
import sys
import subprocess

site_url = "http://localhost"
sysadmin_APIKEY = ""


def check_date_published_in_database():
    """ main function for all processes.
        Look for all organizations.
        Call api of all origanizations to update datasets.
    """
    organizations = get_organizations()
    call_organization_api(organizations)

def get_organizations():
    """ get things easier to use curl  """
    url = "{0}/api/3/action/organization_list".format(site_url)
    command = "curl -X GET -H \"Authorization: {0}\" {1}".format(sysadmin_APIKEY, url)
    response = subprocess.check_output(command, shell=True)
    response = json.loads(response)
    return response.get('result')


def call_organization_api(organizations=[]):
    """ Call CURL to implement before_view of package_show in plugin.py """
    if not organizations:
    	print("There is no organization defined.\n")
    	return
    else:
        for o in organizations:
            command = "curl -X GET -H \"Authorization: {0}\" {1}/organization/{2} > /dev/null".format(sysadmin_APIKEY, site_url, o)
            os.system(command)
            print("Datasets of origanization {0} are updated\n".format(o))

def usage():
    print >> sys.stderr, "Error: Usage: python auto_date_published_cronjob.py <sysadmin_APIKEY>\n"
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()
    sysadmin_APIKEY = sys.argv[1]
    check_date_published_in_database()
    print("Program auto_date_published_cronjob.py exit.\n")
