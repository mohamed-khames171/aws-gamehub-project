# High Availability Game Benchmark & GPU Performance Hub on AWS

A fully scalable, highly available web application deployed on AWS infrastructure. The application dynamically benchmarks GPU performance across popular competitive, sports, and Souls-like titles, logging user interactions to a relational database.

## Architecture Highlights
- **High Availability & Scalability:** Deployed across multiple EC2 instances in different Availability Zones behind an **AWS Application Load Balancer (ALB)** with active health checks.
- **Shared Storage:** Configured **Amazon EFS** mounted at `/mnt/document` for seamless real-time file sharing and application updates between instances.
- **Database Tier:** Powered by **Amazon RDS (PostgreSQL)** for secure, centralized visitor logging and analytics.
- **Reverse Proxy & Security:** Configured **Nginx** as a reverse proxy, enforced SSL/TLS encryption via Certbot, and isolated components using least-privilege **Security Groups**.
- **DNS Routing:** Dynamic DNS integration configured with automated keep-alive updates.

## Tech Stack
- **Cloud Provider:** Amazon Web Services (EC2, ALB, EFS, RDS PostgreSQL, Security Groups)
- **Backend:** Python (Flask), Psycopg2
- **Web Server:** Nginx, Gunicorn / Werkzeug
- **Storage & OS:** Amazon Elastic File System (NFS), Ubuntu Linux
