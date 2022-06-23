from flask import Flask
from flask import request
import mysql.connector
import ast

with open('aws_sql_db_credentials.txt') as file:
    contents = file.read()
    
sql_db_credentials = ast.literal_eval(contents)

# Global variables
sql_user_name = sql_db_credentials['sql_user_name']
sql_password = sql_db_credentials['sql_password']
sql_host_name = sql_db_credentials['sql_host_name']
sql_database_table = sql_db_credentials['sql_database_table']

app = Flask(__name__)

def get_decimal_ip(ip):
    """Database requires we use decimal formatting for the lookup"""
    result = 0
    split_ip = ip.split(".")
    split_ip = [int(x) for x in split_ip]
    result += split_ip[0] * (256**3) 
    result += split_ip[1] * (256**2)
    result += split_ip[2] * (256)
    result += split_ip[3]
    
    return int(result)

def valid_ipv4_check(ip):
    """Improve the efficiency (and save SQL queries) by checking to see if the 
    IP address is valid."""
    decimal_count = 0
    
    
    try: 
        for character in ip:
            if character == '.':
                decimal_count += 1
                
        if decimal_count != 3:
            return False
        
        else:
            subnet_list = ip.split(".")
            subnet_ip_list = [int(x) for x in subnet_list]
            
            for subnet in subnet_ip_list:
                if subnet > 255 or subnet < 0:
                    return False
                else:
                    return True
                
    except:
        return False
            
def get_ip_dict(ip):    
    """This function:
        Checks to see if it's a valid IP address. If it's not, return an error.
        If valid, query the MySQL database and return the fetched data.
        From there, format data into JSON."""
    ipv4_valid = valid_ipv4_check(ip)
    
    if ipv4_valid:
        decimal_ip = get_decimal_ip(ip)

        mydb = mysql.connector.connect(user=sql_user_name, 
                                       password=sql_password, 
                                       host=sql_host_name, 
                                       database=sql_database_table)

        # My database table is named IPv4_v2. Your name will likely vary!
        query = f"""SELECT country_code, country_name, region, city, isp FROM IPv4_v2
                    WHERE ip_from < {decimal_ip}
                    AND ip_to > {decimal_ip} 
                    LIMIT 1"""

        mycursor = mydb.cursor()
        mycursor.execute(query)
        data = mycursor.fetchall()
        
        if len(data) == 0:
            return {'error': f'{ip}: no response for that ip address'}
            
        keys = ["ip", "country_code", "country_name", "region", "city", "isp"]

        # mysql.connector returns database as a list of tuples 
        # with one tuple for each row.
        values = list(data[0]) 
        values = [ip.strip()] + values

        isp_dict = dict(zip(keys, values))
        return isp_dict

    else:
        return {'error': f'{ip}: address is not a valid ipv4 address'}
    
    
@app.route("/ip_fetch")
def fetch_ip():
    """API endpoint to fetch the IP dictionary"""
    
    ip = request.args.get('ip', '')
    ip_dict = get_ip_dict(ip)
    return ip_dict

if __name__ == '__main__':
    app.run(debug=False, port=8000)
