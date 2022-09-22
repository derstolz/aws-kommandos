#!/usr/bin/env python3
from termcolor import colored
from pprint import pprint


class DnsKommandos:
    def __init__(self, route53_client):
        self.route53_client = route53_client

    ## DNS
    ### GETTING ALL HOSTING ZONES
    def get_all_hosted_zones(self):
        return self.route53_client.list_hosted_zones_by_name()['HostedZones']

    ### GETTING A HOSTING ZONE
    def get_hosted_zone(self, hosted_zone_name: str):
        return self.route53_client.list_hosted_zones_by_name(DNSName=hosted_zone_name)['HostedZones'][0]

    ### CREATING DNS RECORDS
    def create_dns_record(self, hosted_zone_name: str,
                          record_type: str,
                          record_value: str,
                          ttl: int):
        hosted_zone = self.get_hosted_zone(hosted_zone_name=hosted_zone_name)
        self.route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone['Id'],
            ChangeBatch={
                'Changes': [
                    {
                        'Action': "UPSERT",
                        'ResourceRecordSet': {
                            'Name': hosted_zone_name,
                            'Type': record_type,
                            'TTL': ttl,
                            'ResourceRecords': [{'Value': record_value}]
                        }
                    }]
            }
        )
        print(colored(f"A new record set {hosted_zone['Name']} {record_type} {record_value} has been created", 'green'))

    ### DELETING DNS RECORDS
    def delete_dns_record(self, hosted_zone_name: str,
                          record_type: str,
                          record_value: str,
                          ttl: int):
        hosted_zone = self.get_hosted_zone(hosted_zone_name=hosted_zone_name)
        try:
            self.route53_client.change_resource_record_sets(
                HostedZoneId=hosted_zone['Id'],
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': "DELETE",
                            'ResourceRecordSet': {
                                'Name': hosted_zone_name,
                                'Type': record_type,
                                'TTL': ttl,
                                'ResourceRecords': [{'Value': record_value}]
                            }
                        }]
                }
            )
            print(colored(f"The record set {hosted_zone['Name']} {record_type} {record_value} has been deleted",
                          'yellow'))
        except Exception as e:
            if "but it was not found" in f"{e}":
                print(colored(f"The record set {record_type} {record_value} for fqdn {hosted_zone_name} "
                              f"has not been found", 'red'))
            else:
                print(f"{type(e)} - {e}")

    ### GETTING RECORD SETS
    def get_record_sets(self, hosted_zone_id: str):
        return self.route53_client.list_resource_record_sets(
            HostedZoneId=hosted_zone_id
        )['ResourceRecordSets']

    ### PRINTING DNS STATS
    def print_hosted_zones(self, verbose: bool = False):
        hosted_zones = self.get_all_hosted_zones()

        if hosted_zones:
            print("Hosting zones are:")
            for zone in hosted_zones:
                hosted_zone_id = zone['Id']
                hz = {
                    'Name': zone['Name'],
                    'HostedZoneId': hosted_zone_id,
                }
                if verbose:
                    hz['ResourceRecordSets'] = self.get_record_sets(hosted_zone_id=hosted_zone_id)
                    pprint(hz, sort_dicts=False)
                else:
                    print(hz)
        else:
            print('No hosting zones found')
