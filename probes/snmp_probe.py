# SNMP probe skeleton using pysnmp (install pysnmp)
from pysnmp.hlapi import *
import os, time
from probes.common import push


def get_snmp(host, community, oid, port=161):
    iterator = getCmd(SnmpEngine(), CommunityData(community), UdpTransportTarget((host, port)), ContextData(), ObjectType(ObjectIdentity(oid)))
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    if errorIndication:
        return None
    elif errorStatus:
        return None
    else:
        return varBinds

if __name__ == '__main__':
    host = os.environ.get('SNMP_HOST', '192.168.1.1')
    community = os.environ.get('SNMP_COMMUNITY', 'public')
    probe_host = os.environ.get('PROBE_HOST', 'probe-1')
    # example OID for ifInOctets
    oids = ['1.3.6.1.2.1.2.2.1.10.1']
    results = {}
    for oid in oids:
        v = get_snmp(host, community, oid)
        results[oid] = str(v)
    payload = {'target': host, 'probe_host': probe_host, 'timestamp': int(time.time()*1000), 'snmp': results}
    code, text = push(payload)
    print('snmp pushed', code)
