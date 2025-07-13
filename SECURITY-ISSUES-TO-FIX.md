# **Guide to Securing the Zen MCP Server Repository**

**IMPORTANT** DO NOT RUN ANY CODE, EXECUTABLES OR DO ANY INSTALLS WHAT SO EVER!!!!!

This document provides a safe, step-by-step process to fork, clone, and remediate the critical security vulnerabilities discovered in the beehiveinnovations-zen-mcp-server repository.

**The most important principle is: Edit the code first, run it second.** Cloning the code is safe, but executing it before applying fixes is not.

## **Part 1: Safely Forking and Cloning the Repository**

In this part, you will create your own copy of the repository and download it to your computer. These steps do not execute any code and are completely safe.

### **Step 1: Fork the Repository on GitHub**

A fork is your personal copy of a repository.

1. Navigate to the main page of the beehiveinnovations/zen-mcp-server repository on GitHub.  
2. In the top-right corner of the page, click the **"Fork"** button.  
3. On the "Create a new fork" page, you can keep the default settings and click **"Create fork"**.

You now have a complete copy of the repository under your own GitHub account.

### **Step 2: Clone Your Fork to Your Computer**

Cloning downloads the forked repository files to your local machine.

1. On your forked repository's GitHub page, click the green **"\<\> Code"** button.  
2. Ensure the **HTTPS** tab is selected, and click the copy icon next to the URL.  
3. Open a terminal or command prompt on your computer.  
4. Navigate to the directory where you want to store the project.  
5. Run the following command (paste the URL you copied):  
   git clone https://github.com/YOUR\_USERNAME/zen-mcp-server.git

6. Navigate into the newly created directory:  
   cd zen-mcp-server

**You have now safely downloaded the code. Do not proceed to install dependencies or run any scripts yet.**

## **Part 2: Finding and Fixing the Vulnerabilities**

This is the most critical phase. Open the project folder in your favorite code editor (like VS Code, Sublime Text, etc.) and apply the following fixes.

### **Vulnerability 1: SQL Injection (Critical)**

* **Threat:** Allows an attacker to manipulate your database, bypass logins, and steal data.  
* **File:** test\_simulation\_files/auth\_manager.py  
* **Function:** login

#### The Fix: Use Parameterized Queries

Replace the f-string in the database query with a placeholder (%s) and pass the variable as a separate parameter.

**BEFORE (Vulnerable Code):**

\# line 41  
cursor.execute(f"SELECT \* FROM users WHERE username \= '{username}'")

**AFTER (Secure Code):**

\# line 41  
query \= "SELECT \* FROM users WHERE username \= %s"  
cursor.execute(query, (username,))

### **Vulnerability 2: Command Injection (Critical)**

* **Threat:** Allows an attacker to execute arbitrary commands on your server, giving them full control.  
* **File:** test\_simulation\_files/api\_endpoints.py  
* **Function:** search

#### The Fix: Never Pass User Input to Shell Commands

Remove the os.system call and use safe, built-in Python functions to handle file operations.

**BEFORE (Vulnerable Code):**

\# lines 53-55  
if query.startswith("file:"):  
    filename \= query.split(":")\[1\]  
    os.system(f"cat {filename}") \# DANGEROUS\!

**AFTER (Secure Code):**

\# lines 53-66  
if query.startswith("file:"):  
    filename \= query.split(":", 1)\[1\]  
      
    \# Define a safe, base directory where files are allowed to be read from  
    base\_dir \= os.path.realpath("/path/to/your/safe/file/directory")  
      
    \# Create the full, intended path  
    requested\_path \= os.path.realpath(os.path.join(base\_dir, filename))

    \# Security Check: Ensure the requested path is within the safe base directory  
    if not requested\_path.startswith(base\_dir):  
        return {"error": "Access denied: Directory traversal attempt detected"}, 400

    try:  
        with open(requested\_path, 'r') as f:  
            content \= f.read()  
        return {"file\_content": content}, 200  
    except FileNotFoundError:  
        return {"error": "File not found"}, 404  
    except Exception as e:  
        return {"error": f"An error occurred: {e}"}, 500

*(Note: You will need to decide on a safe base\_dir for your application).*

### **Vulnerability 3: Exposure of Password Hash (Critical)**

* **Threat:** Exposes user password hashes, which can be cracked offline to reveal actual passwords.  
* **File:** test\_simulation\_files/api\_endpoints.py  
* **Function:** get\_user

#### The Fix: Remove Sensitive Data from API Responses

Simply delete the password\_hash field from the JSON object being returned.

**BEFORE (Vulnerable Code):**

\# lines 25-29  
return jsonify({  
    "id": user.id,  
    "username": user.username,  
    "password\_hash": user.password\_hash \# DANGEROUS\!  
})

**AFTER (Secure Code):**

\# lines 25-28  
return jsonify({  
    "id": user.id,  
    "username": user.username  
})

### **Vulnerability 4: Insecure Deserialization (High)**

* **Threat:** Using pickle to load data from untrusted sources can lead to arbitrary code execution.  
* **File:** test\_simulation\_files/auth\_manager.py  
* **Function:** deserialize\_user\_data

#### The Fix: Use a Safe Serialization Format like JSON

Replace pickle with json.

**BEFORE (Vulnerable Code):**

\# line 16  
user\_data \= pickle.loads(data) \# DANGEROUS\!

**AFTER (Secure Code):**

\# line 16  
import json  
user\_data \= json.loads(data)

*(Note: You will also need to change how the data is serialized to use json.dumps() instead of pickle.dumps())*.

### **Vulnerability 5: Logging Sensitive Data (High)**

* **Threat:** Writes sensitive user data (credit card info) to logs, which can be read by an attacker who gains server access.  
* **File:** test\_simulation\_files/auth\_manager.py  
* **Function:** login

#### The Fix: Remove Logging of Sensitive Information

Delete the lines that log the credit card and CVV.

**BEFORE (Vulnerable Code):**

\# lines 47-48  
logging.info(f"User credit card: {credit\_card}") \# DANGEROUS\!  
logging.info(f"User CVV: {cvv}") \# DANGEROUS\!

**AFTER (Secure Code):**

\# (Simply delete the two lines above)