import sys
import argparse

import ckanapi
import requests

default_tasks = ["existence", "validate_csv"]

class CkanTester():

    def main(self):
        parser = argparse.ArgumentParser(description="AR-KAN CKAN-API validator.")
        parser.add_argument('-b', '--baseurl', type=str, required=True)
        parser.add_argument('-k', '--api-key', type=str, required=False)

        parser.add_argument("-t", '--tasks', type=str, nargs="*", default=default_tasks)

        parser.add_argument("-l", "--list-tasks", type=bool)
        
        args = parser.parse_args()

        if args.list_tasks:
            return default_tasks

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
                    getattr(self, t)(p_meta, r_meta, res_state)
                    print "ran: " + t + " on: " + package
                    report.append(res_state)

        print report

    def existence(self, package_meta, resource_meta, return_state):
        print resource_meta.get("url")
        resp = requests.get(resource_meta.get("url"))
        if resp.status_code in [200,201]:
            return_state["results"]["existence"] = {"result":"valid"}
        else: 
            return_state["results"]["existence"] = {"details":resp.status_code, "result":"not_valid"}

    def validate_csv(self, package_meta, resource_meta, return_state):
        return_state["results"]["validate_csv"] = {"result":"valid"}


if __name__ == '__main__':
    ct = CkanTester()
    ct.main()

