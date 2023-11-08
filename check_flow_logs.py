import boto3
import time
import click

@click.command()
@click.argument('vpc-id', type=str)
@click.argument('log-group-name', type=str)
@click.option('--region', type=str, default='eu-west-2')
@click.option('--max-query-time', type=int, default=60)
def main(vpc_id, log_group_name, region, max_query_time):
    # set start_time to now (seconds since epoch)
    start_time = int(time.time())
    end_time = start_time + max_query_time
    query_string = 'QUERY_STRING'

    # Initialize the CloudWatch Logs client
    client = boto3.client('logs')

    # Start the query
    response = client.start_query(
        logGroupName=log_group_name,
        startTime=start_time,
        endTime=end_time,
        queryString=query_string
    )

    query_id = response['queryId']

    # Wait for the query to complete
    while True:
        query_status = client.get_query_results(
            queryId=query_id
        )['status']
        if query_status == 'Complete':
            break
        elif query_status == 'Failed' or query_status == 'Cancelled':
            print(f"Query failed or was cancelled. Status: {query_status}")
            exit(1)
        time.sleep(1)

    # Retrieve and print the query results
    results = client.get_query_results(
        queryId=query_id
    )['results']

    for result in results:
        print('\t'.join(result))


if __name__ == '__main__':
    main()
