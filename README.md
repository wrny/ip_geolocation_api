# Python IP Geolocation API (built with Flask + MySQL)

Most web services use a visitor's IP address to determine geographic location. Want to know one user's location based on their IP? A one-off search https://whatismyipaddress.com/ip-lookup can work.  But to collect thousands of locations, you need an IP API service. There are dozens of them, and nearly all require monthly SaaS fees and will limit the number of queries you can do. I used to pay for these services and like a lot of SaaS companies, they were generally expensive and terrible. Free services do exist, but it's unwise to depend on them. This code provides a light, performant and low-cost alternative. 

Here's what I did:

1. Purchased a one-time paid-for IP + geographic location database.
2. Uploaded said database to a MySQL db on AWS RDS
3. Wrote a simple Flask API to:

	a. Accept IPv4 ip parameters via get request
	
	b. Confirm it's a valid IPv4 address
	
	c. Transform the IP address into decimal format which the database requires
	
	d. Fetch data from the SQL db via a MySQL query
	
	e. Return the data in a JSON format.  

example: 

`curl http://18.220.202.244:8000/ip_fetch?ip=18.116.242.146`

result:

`{'ip': '18.116.242.146', 'country_code': 'US', 'country_name': 'United States of America', 'region': 'Ohio', 'city': 'Columbus', 'isp': 'Amazon Technologies Inc.'} `

Average response times are between 0.05 - 0.10 seconds (thtat's 1/20th - 1/10th of a second), which is better than most any paid IP API. 

The API itself resides on a standard Ubuntu 20.04 instance on AWS EC2, running Gunicorn and NGINX. 

A video of the tool used in action is below:

[Video](https://drive.google.com/file/d/1ixz7utEgVPvY63bp7LYyV2I5yQWtXltA/view?usp=sharing "Video")

## Deployment instructions for Ubuntu 20.04 on AWS:

**First**:
* Buy a geolocation database with the proper licensing and upload it to an AWS MySQL RDS.

**In AWS**: 
* Create a standard EC2 instance Ubuntu 20.04. I chose a t2.micro instance.
* Go to security security groups for the instance and open port 8000 to inbound traffic.

**In the instance (access via SSH, Remina, PuTTY, etc.)**

`sudo apt update`

`sudo apt upgrade`

`sudo git clone https://www.github.com/wrny/ip_geolocation_api`

`cd ip_geolocation_api`

`sudo apt-get install python3.8-venv`

`sudo apt-get install python3-pip`

`sudo python3 -m venv venv`

`source venv/bin/activate`

`sudo pip3 install -r requirements.txt`

`sudo pip3 install gunicorn`

`pkill gunicorn`

Create a text document containing a dictionary with your AWS credentials. The real keys and fake values are below.

`{'sql_user_name' : 'USERNAME HERE', 'sql_password' : 'PASSWORD HERE', 'sql_host_name' : HOST ADDRESS HERE', 
'sql_database_table' : 'DATABASE NAME HERE'}`

Name the file: "aws_sql_db_credentials.txt"

**Setting up NGINX**

`sudo apt install nginx`

`sudo nano /etc/nginx/sites-enabled/ip_geolocation_api`

* You'll get a blank file. Paste what's below with the proper IP address where it reads YOUR_IP_ADDRESS_HERE.

> server {
&emsp; listen 80;
&emsp;server_name YOUR_IP_ADDRESS_HERE;
&emsp;location / {
&emsp;&emsp;proxy_pass http://127.0.0.1:8000;
&emsp;&emsp;proxy_set_header Host $host;
&emsp;&emsp;proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
&emsp;}
}


`sudo unlink /etc/nginx/sites-enabled/default`

`sudo nginx -s reload`

**Activate the API**

`tmux`

`gunicorn -b 0.0.0.0:8000 main:app`

And it's done.

To test

`curl http://18.220.202.244:8000/ip_fetch?ip=18.116.242.146`

result should be:

`{'ip': '18.116.242.146', 'country_code': 'US', 'country_name': 'United States of America', 'region': 'Ohio', 'city': 'Columbus', 'isp': 'Amazon Technologies Inc.'}`

**Note**: I'm not looking to build a business off of this tool, because the database license does not permit it. This is solely an academic exercise. I'll will be taking down the live API at some point.
