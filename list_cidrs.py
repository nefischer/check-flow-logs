import boto3
import click

# Function to get security groups with inbound rules where the source CIDR is not the default value
def get_unmanaged_inbound_rules(region, default_cidr, sg_id):
    # Create an EC2 resource session
    ec2 = boto3.client('ec2', region_name=region)

    try:
        sg_info = ec2.describe_security_groups(GroupIds=[sg_id])
        if sg_info['SecurityGroups']:
            security_group = sg_info['SecurityGroups'][0]
            non_default_rules = []

            # Filter security groups for non-default inbound rules
            for permission in security_group.get('IpPermissions', []):
                # Check if the IpRanges list is not empty and the CIDR is not the default value
                non_default_cidr_ips = [
                    ip_range.get('CidrIp')
                    for ip_range in permission.get('IpRanges', [])
                    if ip_range.get('CidrIp') != default_cidr
                ]
                if non_default_cidr_ips:
                    non_default_rules.append({
                        'IpProtocol': permission.get('IpProtocol'),
                        'FromPort': permission.get('FromPort'),
                        'ToPort': permission.get('ToPort'),
                        'CidrIp': non_default_cidr_ips
                    })

        return non_default_rules
    except Exception as e:
        click.echo(f"Error: {str(e)}")



@click.command()
@click.argument('managed-cidr', type=str)
@click.argument('sg-id', type=str)
@click.argument('region', default='eu-west-2')
def main(managed_cidr, sg_id, region):
    # Get the non-default inbound security rules
    inbound_rules = get_unmanaged_inbound_rules(region=region, managed_cidr=managed_cidr, sg_id=sg_id)

    # Output the non-default inbound rules
    for rule in inbound_rules:
        print(rule)


if __name__ == '__main__':
    main()
