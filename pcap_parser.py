from pcapkit import IP, extract,HTTP
import argparse
import logging

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pcap_file',type=str,required=True)

    return parser.parse_args()

########## Configuration ##########
logger=logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
args = get_args()

## Read Files
extraction = extract(fin=args.pcap_file, store=False, nofile=True,tcp=True,strict=True)
for datagram in extraction.reassembly.tcp:
    if datagram.packet is not None and HTTP in datagram.packet:
        logging.info('{}'.format(datagram.packet[HTTP]))

                     


