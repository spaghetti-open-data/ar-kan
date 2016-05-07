import sys
import argparse

import ckanapi
import requests

def main():
    parser = argparse.ArgumentParser(description="AR-KAN CKAN-API validator.")
    parser.add_argument('-b', '--baseurl', type=str, required=True)
    parser.add_argument('-k', '--api-key', type=str, required=False)

    parser.add_argument("-t", '--tasks', type=str, nargs="*", default=["existence"])

    parser.add_argument("-l", "--list-tasks", type=bool)
    
    args = parser.parse_args()

    if args.list_tasks:
        return ["existence", "validate_csv"]

    baseurl = args.baseurl
    api_key = args.api_key


    print "connecting: " + baseurl
    ckan = ckanapi.RemoteCKAN(baseurl,
        apikey = api_key,
        user_agent='ckanapivalidator/1.0 (+'+baseurl+')')
    print "connected: " + baseurl

    report = []

    for package in ckan.action.package_list():
        p_meta = ckan.action.package_show(id=package)
        for resource in p_meta.get("resources"):
            r_meta = ckan.action.resource_show(id=resource.get("id"))
            for t in args.tasks:
                print "running: " + t + " on: " + package
                res_state = {"results":{}, "package":p_meta, "resource":r_meta}
                existence(p_meta, r_meta, res_state)
                validate_csv(p_meta, r_meta, res_state)
                print "ran: " + t + " on: " + package
                report.append(res_state)

    print report


def existence(package_meta, resource_meta, return_state):
    print package_meta
    print resource_meta
    resp = requests.get(resource_meta.get("url"))
    print resp
    return_state["results"]["existence"] = "valid"

def validate_csv(package_meta, resource_meta, return_state):
    return_state["results"]["validate_csv"] = "valid"



if __name__ == '__main__':
    main()

