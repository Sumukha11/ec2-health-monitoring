# ec2-health-monitoring

EC2 Health Monitoring and Alerting System

Description:
This project is a lightweight EC2 health monitoring solution that automates resource tracking, anomaly detection, and alerting for AWS EC2 instances. It is built using Python, AWS CloudWatch, SNS, Docker, and cron, and mimics a production-grade monitoring setup.

Features:
- Automated health checks for:
  - CPU utilization (via AWS CloudWatch API)
  - Memory and Disk usage (via Linux shell commands)
  - Docker container runtime status
- Sends alerts using AWS SNS when resource usage crosses thresholds
- Pushes custom metrics (memory and disk usage) to AWS CloudWatch
- Configured to run every 2 minutes using cron jobs
- CloudWatch Dashboard created to visualize metrics using Gauge and Number widgets

Technologies Used:
- AWS EC2
- AWS CloudWatch
- AWS SNS
- Docker
- Python (boto3, subprocess)
- Linux Crontab

Project Structure:
monitor.py                - Main monitoring and alerting script
crontab-setup.md          - Setup instructions for cron job
dashboard-screenshot.png  - Screenshot of CloudWatch dashboard
sns-alert-example.png     - Screenshot of SNS email alert
README.txt                - This project description file

Use Case:
This project simulates real-world EC2 health monitoring and alerting, making it ideal for DevOps engineers or cloud practitioners looking to build cost-effective monitoring solutions without third-party tools.

Setup Instructions:
1. Launch an EC2 instance (Ubuntu)
2. Attach an IAM Role with the following permissions:
   - cloudwatch:GetMetricStatistics
   - cloudwatch:PutMetricData
   - sns:Publish
3. Install Python 3 and Docker on the instance
4. Deploy a dummy Docker container using:
   docker run -d --name ec2-health-test ubuntu sleep infinity
5. Upload the monitor.py script to the instance
6. Edit monitor.py to update:
   - INSTANCE_ID
   - SNS_TOPIC_ARN
7. Schedule the script using crontab:
   crontab -e
   */2 * * * * /usr/bin/python3 /home/ubuntu/health-check/monitor.py
8. Create a CloudWatch Dashboard and add widgets for:
   - CPUUtilization (Number)
   - MemoryUsage (Gauge)
   - DiskUsage (Gauge)
   - DockerStatus (Number or Text/Log if needed)
9. Observe alerts via email and monitor real-time metrics on the dashboard

