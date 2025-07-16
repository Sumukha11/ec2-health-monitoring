import boto3
import subprocess
from datetime import datetime, timedelta, timezone

# AWS Configuration
REGION = '#Region'
INSTANCE_ID = 'EC2 ID'
SNS_TOPIC_ARN = '#Add the ARN'

cloudwatch = boto3.client('cloudwatch', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

def send_alert(subject, message):
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        print(f"Alert sent: {subject}")
    except Exception as e:
        print(f"Failed to send SNS alert: {e}")

# Time window for CloudWatch metric statistics
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(minutes=10)

# CPU Utilization
print("EC2 CPU Utilization:")
try:
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=['Average']
    )

    for data in response['Datapoints']:
        cpu_avg = data['Average']
        print(f"Timestamp: {data['Timestamp']} - Average CPU: {cpu_avg:.2f}%")
        if cpu_avg > 70:
            send_alert(
                subject="High CPU Usage Detected",
                message=f"CPU usage is {cpu_avg:.2f}% on instance {INSTANCE_ID}"
            )
except Exception as e:
    print(f"Error fetching CPU metrics: {e}")
    send_alert("CPU Metric Fetch Error", str(e))

# Memory Usage
print("\nEC2 Memory Usage:")
try:
    mem_output = subprocess.check_output("free -m | grep Mem", shell=True, text=True)
    total, used, free, *_ = map(int, mem_output.split()[1:4])
    used_percent = (used / total) * 100
    print(f"Total: {total} MB | Used: {used} MB | Free: {free} MB | Usage: {used_percent:.2f}%")

    # Push memory usage metric
    cloudwatch.put_metric_data(
        Namespace='Custom/EC2Health',
        MetricData=[
            {
                'MetricName': 'MemoryUsagePercent',
                'Dimensions': [{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
                'Value': used_percent,
                'Unit': 'Percent'
            }
        ]
    )

    if used_percent > 80:
        send_alert(
            subject="High Memory Usage Detected",
            message=f"Memory usage is {used_percent:.2f}% on instance {INSTANCE_ID}"
        )
except Exception as e:
    print(f"Error fetching memory usage: {e}")
    send_alert("Memory Check Error", str(e))

# Disk Usage
print("\nEC2 Disk Usage (/ partition):")
try:
    disk_output = subprocess.check_output("df -h / | tail -1", shell=True, text=True)
    parts = disk_output.split()
    if len(parts) >= 6:
        _, size, used, avail, percent_str, _ = parts[:6]
        percent = int(percent_str.strip('%'))
        print(f"Size: {size} | Used: {used} | Available: {avail} | Usage: {percent_str}")

        # Push disk usage metric
        cloudwatch.put_metric_data(
            Namespace='Custom/EC2Health',
            MetricData=[
                {
                    'MetricName': 'DiskUsagePercent',
                    'Dimensions': [{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
                    'Value': percent,
                    'Unit': 'Percent'
                }
            ]
        )

        if percent > 75:
            send_alert(
                subject="High Disk Usage Detected",
                message=f"Disk usage is {percent}% on instance {INSTANCE_ID}"
            )
    else:
        print("Unexpected output format from df command.")
except Exception as e:
    print(f"Error fetching disk usage: {e}")
    send_alert("Disk Check Error", str(e))

# Docker Container Status
print("\nDocker Container Status:")
try:
    output = subprocess.check_output(
        ['docker', 'ps', '--format', '{{.Names}}: {{.Status}}'],
        text=True
    )

    container_running = False
    for line in output.strip().splitlines():
        name, status = line.split(": ", 1)
        print(f"{name}: {status}")
        if name == "ec2-health-test" and status.startswith("Up"):
            container_running = True

    # Push container status metric: 1 if running, 0 if not
    docker_metric = 1 if container_running else 0
    cloudwatch.put_metric_data(
        Namespace='Custom/EC2Health',
        MetricData=[
            {
                'MetricName': 'DockerContainerRunning',
                'Dimensions': [{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
                'Value': docker_metric,
                'Unit': 'Count'
            }
        ]
    )

    if not container_running:
        send_alert(
            subject="Docker Container Stopped",
            message=f"The container 'ec2-health-test' is not running on instance {INSTANCE_ID}."
        )
except subprocess.CalledProcessError as e:
    print(f"Error checking Docker containers: {e}")
    send_alert("Docker Check Error", str(e))
