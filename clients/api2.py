# core
import logging
import os
import tempfile
import re
import json
import argparse
import time

# non-core
import requests

DEFAULT_SM_USER='junk@sillit.com'
DEFAULT_SM_PASSWORD='FJRbnz'
DEFAULT_BASE_URL='https://beta.swissmodel.expasy.org'

logging.basicConfig(
        format='%(asctime)-12s %(lineno)3d: %(levelname)-8s %(message)s',
        level=logging.INFO)
LOG = logging.getLogger(__name__)

class SmAlignmentData(object):

    def __init__(self, *, target_sequence, template_sequence, template_seqres_offset, 
            pdb_id, auth_asym_id, assembly_id=None, project_id=None):
        self.target_sequence = target_sequence
        self.template_sequence = template_sequence
        self.template_seqres_offset = template_seqres_offset
        self.pdb_id = pdb_id
        self.auth_asym_id = auth_asym_id
        self.assembly_id = assembly_id
        self.project_id = project_id

    @classmethod
    def load(cls, infile):
        try:
            data = json.load(infile)
        except Exception as err:
            raise Exception("failed to load SmAlignment from json file {}: {}".format(infile, err))
        if 'meta' in data:
            del data['meta']
        return cls(**data)

    def to_dict(self):
        data = self.__dict__
        data = dict((k, v) for k, v in data.items() if v != None)
        return data

class SmClient(object):
    """
    Client for API 2 (SWISSMODEL)

    https://beta.swissmodel.expasy.org/swagger/

    Note: get detailed logs by setting environment var CATHSM_DEBUG=1
    """

    def __init__(self, *, base_url=DEFAULT_BASE_URL):

        self.base_url = base_url
        self.submit_url = '{}/alignment/'.format(self.base_url)
        self.headers = {}

    def submit(self, aln):

        request_data = aln.to_dict()
        
        LOG.debug("Request.URL:  {}".format(self.submit_url))
        LOG.debug("Request.DATA: {}".format(request_data))
        r = requests.post(self.submit_url, data=request_data, headers=self.headers)
        if r.status_code != 201:
            LOG.error("Error: failed to submit data: status = {} (expected 201), text = {}".format(r.status_code, r.text))
            r.raise_for_status()

        try:
            response_data = r.json()
        except:
            LOG.error("failed to get json from response: {}".format(r))
            raise

        return response_data

    def status(self, project_id):

        status_url = '{}/alignment/{}/status/'.format(self.base_url, project_id)
        r = requests.get(status_url, headers=self.headers)
        response_data = r.json()
        
        return response_data

    def results(self, project_id):

        status_url = '{}/alignment/{}'.format(self.base_url, project_id)
        r = requests.get(status_url, headers=self.headers)
        response_data = r.json()

        return response_data

    def authenticate(self, *, sm_user=None, sm_pass=None):
        data = { 'username': sm_user, 'password': sm_pass }
        LOG.debug('get_auth_headers.data: {}'.format(data))
        headers = { 'accept': 'application/json' }
        r = requests.post(self.base_url + '/api-token-auth/', data=data, headers=headers)
        LOG.debug( "auth_response [{}]: {}".format(r.status_code, r.json()))
        response_data = r.json()
        headers = {'Authorization': 'token {}'.format(response_data['token'])}
        self.headers = headers

def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--in', type=str, required=True, dest='infile', help='input data file (json)')
    parser.add_argument('--out', type=str, required=True, dest='outfile', help='output PDB file')
    parser.add_argument('--user', type=str, required=False, dest='sm_user', help='specify sm user')
    parser.add_argument('--pass', type=str, required=False, dest='sm_pass', help='specify sm password')
    parser.add_argument('--sleep', type=float, default=10, dest='sleep', help='waiting time between requests')
    args = parser.parse_args()

    sm_user = DEFAULT_SM_USER
    if args.sm_user:
        sm_user = args.sm_user
    elif 'SM_USER' in os.environ:
        sm_user = os.environ['SM_USER']
     
    sm_pass = DEFAULT_SM_PASSWORD
    if args.sm_pass:
        sm_pass = args.sm_pass
    elif 'SM_PASSWORD' in os.environ:
        sm_pass = os.environ['SM_PASSWORD']

    with open(args.infile) as infile:
        aln_data = SmAlignmentData.load(infile)

    LOG.info("IN:  {}".format(args.infile))
    LOG.info("OUT: {}".format(args.outfile))

    LOG.info("Initialising Client ...")
    client = SmClient()
   
    LOG.info("Authenticating ... ")
    client.authenticate(sm_user=sm_user, sm_pass=sm_pass)
    
    LOG.info("Submitting data ... ")
    submit_r = client.submit(aln_data)
    project_id = submit_r['project_id']
    
    LOG.info("Checking status of project <{}> ...".format(project_id))
    while True:
        status_r = client.status(project_id)
        status = status_r['status']
        LOG.info("   status: {}".format(status) )
        if status == 'COMPLETED':
            break
        else:
            time.sleep(args.sleep)

    LOG.info("Retrieving results ... ")
    result_r = client.results(project_id)
    
    LOG.debug("result: {}".format(result_r))
    coords = result_r['coordinates']
    
    LOG.info("Writing coordinates to {}".format(args.outfile))
    with open(args.outfile, 'w') as outfile:
        outfile.write(coords)

if __name__ == '__main__':
    main()
