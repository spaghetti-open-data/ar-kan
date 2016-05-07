import sys
import argparse

import ckanapi

def main():
	parser = argparse.ArgumentParser(description="AR-KAN CKAN-API validator.")
	parser.add_argument('-b', '--baseurl', type=str, required=True)
	parser.add_argument('-k', '--api-key', type=str, required=True)

	parser.add_argument("-t", '--tasks', type=str, nargs="*")
	
	args = parser.parse_args()

	baseurl = args.baseurl
	api_key = args.api_key


	print "connecting: " + baseurl
	ckan = ckanapi.RemoteCKAN(baseurl,
		apikey = api_key,
		user_agent='ckanapivalidator/1.0 (+'+baseurl+')')
	print "connected: " + baseurl

	for t in args.tasks:
		print "running: " + t


if __name__ == '__main__':
	main()

