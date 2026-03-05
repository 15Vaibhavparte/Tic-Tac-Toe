<img width="1911" height="1069" alt="Screenshot 2026-03-05 201759" src="https://github.com/user-attachments/assets/889c7f10-c4d5-41eb-b0d3-7d2798c39b3d" /># AWS Serverless & Observability Trial: Multiplayer Tic-Tac-Toe ☁️🎮

A hands-on exploration of AWS serverless architecture and cloud observability. This project was built as a technical "trial" to understand how distributed AWS services communicate in a real-time environment.

---

## 🏗️ Part 1: Serverless Architecture & System Design
The goal of this phase was to build a logic-heavy application with zero server management, focusing on event-driven compute and NoSQL data modeling.

### **Service Breakdown & Setup Steps**

#### **1. Amazon S3 (Static Website Hosting)**
* **Description:** Used to host the frontend HTML, CSS, and JavaScript files globally without a web server.
* **Setup Steps:**
    1. Create a bucket with a globally unique name.
    2. Uncheck "Block all public access" and acknowledge the warning.
    3. Enable "Static website hosting" in the Properties tab.
    4. Add a Bucket Policy (JSON) to allow `s3:GetObject` for public read access.
<img width="1914" height="1079" alt="Screenshot 2026-03-05 204746" src="https://github.com/user-attachments/assets/8c55ada3-97e4-41ea-a0c6-96b7e9965ce4" />


#### **2. Amazon DynamoDB (NoSQL Database)**
* **Description:** A key-value database used to store user profiles and active game states.
* **Setup Steps:**
    1. Create a table `TicTac-Users` (Partition Key: `email`).
    2. Create a table `TicTac-Games` (Partition Key: `gameId`).
    3. **Crucial:** Add Global Secondary Indexes (GSI) for `playerX` and `playerO` to allow querying games by player identity instead of just the Room Code.

<img width="1910" height="1076" alt="Screenshot 2026-03-05 192054" src="https://github.com/user-attachments/assets/e7ed27cf-9b16-4ac1-bc07-b3adced766bf" />
<img width="1910" height="1067" alt="Screenshot 2026-03-05 192105" src="https://github.com/user-attachments/assets/2746a03c-bbbd-4f43-80e9-d25bbc901616" />
<img width="1913" height="1065" alt="Screenshot 2026-03-05 195711" src="https://github.com/user-attachments/assets/297e8234-947b-464a-8255-1f211f936360" />
<img width="1919" height="1069" alt="Screenshot 2026-03-05 195836" src="https://github.com/user-attachments/assets/ead42bb8-067f-4541-8f91-26f9cc43d49d" />
<img width="1907" height="1072" alt="Screenshot 2026-03-05 195817" src="https://github.com/user-attachments/assets/dbcaf4ba-1f68-4fa2-be66-75b6d2de384c" />


#### **3. AWS Lambda (Serverless Compute)**
* **Description:** The "Brain" of the app. It runs Python code in response to API triggers to manage game logic.
* **Setup Steps:**
    1. Create a function from scratch using Python 3.x.
    2. Update the Execution Role to include permissions for DynamoDB access.
    3. Deploy the backend logic using the `boto3` library to communicate with the database.
<img width="1920" height="2026" alt="FireShot Capture 050 - TicTacToeLogic - Functions - Lambda -  ap-south-1 console aws amazon com" src="https://github.com/user-attachments/assets/94ac386f-e01e-4f68-9b4f-bf3c853c1c4a" />


#### **4. Amazon API Gateway (REST API)**
* **Description:** The entry point that connects the frontend to the Lambda function.
* **Setup Steps:**
    1. Create a REST API.
    2. Create a `/{proxy+}` resource with an `ANY` method.
    3. Enable **Lambda Proxy Integration**.
    4. **Crucial:** Enable **CORS** (Cross-Origin Resource Sharing) so the S3 website can talk to the API.
    5. Deploy the API to a `dev` stage to get the Invoke URL.
<img width="1913" height="1072" alt="Screenshot 2026-03-05 192707" src="https://github.com/user-attachments/assets/b8750b3b-5179-44cc-a84f-f4e9e9b5774f" />

---
Serverless Architecture in Action**
*A split-screen demonstration of real-time matchmaking, 4-digit room code generation, and synchronized game state.*
https://github.com/user-attachments/assets/95e2d28b-26b6-42b6-b4d0-9ede3edd95fe



## 📈 Part 2: DevOps, Automation & Observability
This phase focuses on maintaining system health and automating the deployment lifecycle.

### **Service Breakdown & Setup Steps**

#### **5. AWS CodePipeline (CI/CD)**
* **Description:** Automates the movement of code from GitHub to the live AWS environment.
* **Setup Steps:**
    1. Create a pipeline and connect it to your GitHub repository.
    2. Set the Source to trigger on every `push` to the `main` branch.
    3. (Optional) Add a **CodeBuild** stage to run a Python linter (flake8) to check for syntax errors.
    4. Add a Deploy stage targeting your S3 bucket (ensure "Extract before deploying" is checked).
<img width="1915" height="1075" alt="Screenshot 2026-03-05 200942" src="https://github.com/user-attachments/assets/de637eb6-6300-4b8c-a564-91ffed9ca664" />
<img width="1919" height="1079" alt="Screenshot 2026-03-05 200953" src="https://github.com/user-attachments/assets/b61d181b-cede-4fcf-b3ee-3cb1595c04ce" />



#### **6. Amazon CloudWatch (Monitoring)**
* **Description:** Provides real-time metrics and logging for the entire stack.
* **Setup Steps:**
    1. **Dashboards:** Create a dashboard and add widgets for Lambda Invocations and DynamoDB Read Capacity Units.
    2. **Alarms:** Create a Metric Alarm for "Lambda Errors > 0".
    3. **Configuration:** Set "Treat missing data as good" to ensure the alarm stays "OK" when no errors are present.
<img width="1919" height="1079" alt="Screenshot 2026-03-05 203119" src="https://github.com/user-attachments/assets/02928d78-941b-4921-97d4-e820b00f60d8" />


#### **7. Amazon SNS (Simple Notification Service)**
* **Description:** Used to send automated alerts when the system health degrades.
* **Setup Steps:**
    1. Create a Standard Topic (e.g., `TicTac-Alerts`).
    2. Create an Email Subscription and confirm the link sent to your inbox.
    3. Link this SNS Topic to your CloudWatch Alarm.
<img width="1911" height="1069" alt="Screenshot 2026-03-05 201759" src="https://github.com/user-attachments/assets/93bf0548-711b-4c84-bb66-1173e5fd3167" />
<img width="1911" height="1071" alt="Screenshot 2026-03-05 202005" src="https://github.com/user-attachments/assets/7e43851a-8e99-4e18-9bea-4fd1ada51da4" />
<img width="1917" height="1076" alt="Screenshot 2026-03-05 195321" src="https://github.com/user-attachments/assets/729491f6-0959-4cde-bb89-652f0475bf85" />

CI/CD & Observability in Action**
*A demonstration of the "Push-to-Live" workflow via AWS CodePipeline and real-time health monitoring in CloudWatch.*
https://github.com/user-attachments/assets/2ed21de2-c526-4139-b5a0-361361bd3736


---
