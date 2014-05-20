#!/usr/bin/python
"""
handler for sos responses from neptune
"""
import httplib2
import json
import requests
import ast
import yaml
import logging
from gevent.pywsgi import WSGIServer
import json
from bs4 import * 

__author__ = "abird"

class Handler():
    def __init__(self):

        logger = logging.getLogger('importer_service')
        hdlr = logging.FileHandler('importer_service.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.DEBUG)

        self.logger = logger
        self.logger.info("Setting up neptune handler service...")

        self.startup()

    def startup(self):  

        stream = open("./extern.yml", 'r')
        ion_config = yaml.load(stream)

        self.PORT = ion_config['eoi']['neptune_sos_handler']['port']
        self.logger.info('Serving Neptune Handler on '+str(self.PORT)+'...')
        server = WSGIServer(('', self.PORT), self.application).serve_forever()


    def get_caps(self):
        pass

    def application(self, env, start_response):

            request = env['PATH_INFO']
            request_query = env['QUERY_STRING']
            print "request:"+request
            print "query:"+request_query
            if request == '/' and (len(request_query) > 2):
                request = request_query
                print "modifying request...."

            #make sure the fields are lowers
            params = request.split("&")
            query_array =[]
            for param in params:
                create_query = ""
                fields = param.split("=")
                create_query+=fields[0].lower()
                create_query+="="
                create_query+=fields[1]
                query_array.append(create_query)

            request = "&".join(query_array)


            if request == '/' and (len(request_query) > 2):
                request = request_query

            if request == '/':
                start_response('404 Not Found', [('Content-Type', 'application/xml')])
                return ["<h1>Error<b>please add request information</b>"]
            elif "service=SOS" not in request:   
                start_response('404 Not Found', [('Content-Type', 'application/xml')])
                return ["<h1>Not an sos service request</b>"]
            else:
                if request.startswith("/?"):
                    request = request[2:]
                elif request.startswith("/"):
                    request = request[1:]

                print "request:"+request
                split_request = request.split("&")
                print "request:", split_request

                output = ''         
                #print "env:"+str(env)
                neptune_sos_link = "http://dmas.uvic.ca/sos?"+str(request)
                print neptune_sos_link              
                r_text = requests.get(neptune_sos_link)

                print "---end of request---"
                #fix the crs code
                soup = BeautifulSoup(r_text.text,"xml")

                get_caps = True
                for get_req in soup.findAll("Get"):
                    if get_caps:
                        get_caps = False
                    else:
                        get_req.extract()
                

                for env in soup.findAll("Envelope"):
                    env['srsName'] = "urn:ogc:def:crs:EPSG:6.5:4326" 
                
                    
                response_headers = [('Content-Type', 'application/xml; charset=utf-8')]
                status = '200 OK'
                #remove the html codes i
                html_start = "<html><body>"
                html_end = "</body></html>"
                xml_response = str(soup)
                if xml_response.startswith(html_start):
                    xml_response = xml_response.replace(html_start, "");
                if xml_response.endswith(html_end): 
                    xml_response = xml_response.replace(html_end,"");

                print "-------output---------"
                #print "xmlresp:\n"+xml_response[:]
                start_response(status, response_headers)
                return [xml_response]
            
