import sys
import argparse
from datetime import datetime

import ckanapi
import requests

default_tasks = ["existence", "validate_csv"]

class CkanTester():

    def main(self):
        parser = argparse.ArgumentParser(description="AR-KAN CKAN-API validator.")
        parser.add_argument('-b', '--baseurl', type=str, required=True)
        parser.add_argument('-k', '--api-key', type=str, required=False)
        parser.add_argument('-p', '--package', type=str, required=False)
        
        parser.add_argument("-t", '--tasks', type=str, nargs="*", default=default_tasks)

        parser.add_argument("-l", "--list-tasks", action="store_true")
        
        args = parser.parse_args()

        if args.list_tasks:
            print default_tasks
            return

        baseurl = args.baseurl
        api_key = args.api_key


        print "connecting: " + baseurl
        ckan = ckanapi.RemoteCKAN(baseurl,
            apikey = api_key,
            user_agent='ckanapivalidator/1.0 (+'+baseurl+')')
        print "connected: " + baseurl

        report = []
        packages = []
        if args.package:
            packages = [ args.package ]
        else:
            packages = ckan.action.package_list()
            
        for package in packages:
            print "processing package: " + package
            p_meta = ckan.action.package_show(id=package)
            for resource in p_meta.get("resources"):
                print "processing resource: " + resource.get("name") + " (" + resource.get("id") + ")"
                r_meta = ckan.action.resource_show(id=resource.get("id"))
                res_state = {"results":{}, "package":p_meta, "resource":r_meta}
                for t in args.tasks:
                    print "running: " + t + " on: " + package
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
        if return_state["results"]["existence"]["result"] != "valid":
            return_state["results"]["validate_csv"] = {"result":"not_valid", "details":"not applicable"}
        else:
            return_state["results"]["validate_csv"] = {"result":"valid"}

    def check_timestamp(self, package_meta, resource_meta, return_state):
        print resource_meta.get("revision_timestamp")
        if not resource_meta.get("revision_timestamp"):
            return_state["results"]["timestamp"] = {"details":"No revision timestamp", "result":"not_valid"}
            return
        
        resp = requests.head(resource_meta.get("url"))
        #'Last-Modified': 'Fri, 21 Aug 2015 10:55:10 GMT'
        last_modified = datetime.strptime(resp.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z")
        
        #u'revision_timestamp': u'2014-10-13T12:48:21.574327'
        rev_ts = datetime.strptime(resource_meta.get("revision_timestamp"), "%Y-%m-%dT%H:%M:%S.f")

        if last_modified < rev_ts:
            return_state["results"]["timestamp"] = {"details":"Resource older than revision timestamp", "result":"not_valid"}
        else: 
            return_state["results"]["timestamp"] = {"result":"valid"}
		

if __name__ == '__main__':
    ct = CkanTester()
    ct.main()

