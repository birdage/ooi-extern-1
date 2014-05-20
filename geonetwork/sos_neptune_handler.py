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

    def application(self,env, start_response):

            request = env['PATH_INFO']       
            
            if request == '/':
                start_response('404 Not Found', [('Content-Type', 'application/xml')])
                return ["<h1>Error<b>please add request information</b>"]
            elif "service=SOS" not in request:   
                start_response('404 Not Found', [('Content-Type', 'application/xml')])
                return ["<h1>Not an sos service request</b>"]
            else:

                print "query:" + env['QUERY_STRING']               
                request = request[1:]

                print "request:"+request
                split_request = request.split("&")
                print "request:",split_request


                request2 = env['QUERY_STRING']
                if len(request2) > 1:
                    request = request2


                output = ''         
                #print "env:"+str(env)
                neptune_sos_link = "http://dmas.uvic.ca/sos?"+str(request)
                print neptune_sos_link              
                r_text = requests.get(neptune_sos_link)

                print "---end of request---"
                #fix the crs code
                soup = BeautifulSoup(r_text.text,"xml")
                
                for get_req in soup.findAll("Get"):
                    get_req.extract()
                

                for env in soup.findAll("Envelope"):
                    env['srsName'] = "urn:ogc:def:crs:EPSG:6.5:4326" 
                    
                
                text_file = open("/Users/rpsdev/ooi-extern/Output.html", "w")
                text_file.write("%s" % str(soup))
                text_file.close()
                
                    
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
            
