# DocScan
DocScan is a comprehensive full stack web application that Scans Documents for similarity with an inbuilt credit system.

## System Architecture:

**User Flow**

| Step | Description |
|---|---|
| **1** | User opens frontend in browser. |
| **2** | User logs in or registers. |
| **3** | User uploads document for scanning. |
| **4** | Frontend sends request to Flask backend. |
| **5** | Flask handles document storage, matching, and credit deduction. |
| **6** | Matched documents and results are sent back to frontend. |
| **7** | Admin can log in to view analytics and approve credit requests. |

## Architecture

```mermaid
flowchart TB
    user((User)) -->|Open Website| frontend[Frontend - HTML/CSS/JS]
    admin((Admin)) -->|Login| backend[Flask API]
    swagger((Swagger UI)) -->|/apidocs| backend
    cronjob((Daily CronJob)) -->|Runs at Midnight| backend

    frontend -->|User Login/Signup| backend
    backend -->|Auth Check| database[SQLite DB]
    backend -->|Credits Check| database
    frontend -->|Uploads Document| backend
    backend -->|Stores Document| storage[Persistent Volume]
    backend -->|Processes Document - AI Match| matcher[Document Matcher]
    matcher --> backend
    backend -->|Returns Results| frontend
    backend -->|Logs Scan| database
    admin -->|View Analytics| backend
    backend -->|Fetch Data| database
    backend -->|Resets Credits| database
```
**Deployment Approach**

The plan involves containerizing the application using Docker and orchestrating it with Kubernetes. A Helm chart defines the necessary resources:

- A Deployment for running the Flask-based service.
- A Service to expose the application within the cluster.
- A PersistentVolumeClaim (PVC) for storing the SQLite database and uploaded documents.
- A CronJob to reset user credits daily.
- After building and pushing the Docker image to a container registry, the Helm chart can be installed on a cluster (e.g., Minikube). The application becomes accessible through the configured service endpoint, and Swagger UI is available at /apidocs.

Credit reset functionality:
- A cronjob will be deployed as part of the helm chart
- Every day the job is triggered, resetting the credits (Deployment instructions given below)

How to deploy and test locally:
- Methode 1
  - Pre-requisites: python,pip installed locally
  - Clone the repo
  - Open terminal and cd into the repo
  - python -m venv venv
  - venv\Scripts\activate
  - pip install -r requirements.txt
  - python app.py
    
- Methode 2
  - Pre-requisites: Docker desktop installed
  - docker pull vishalvn2003492/docscan:v1
  - docker run -d -p 8080:80 vishalvn2003492/docscan:v1
  - open localhost:8080 in browser
 
- Methode 3
  - A kubernetes environment, like minikube or a kubernetes cluster
  - cd into docscanner in charts folder in repo
  - helm install doscanner . , given that the kuberneted env is accessible in cmd, powershell or equivalent
  - This deploys a service, to access docscan, cronjob for credit reset, the deployment itself
  - Port forward the service using kubectl command, kubectl port-forward service/document-scanner-service
  - Or use a ui like lens (openlens) and port forward, access the ui

Screenshots:
![image](https://github.com/user-attachments/assets/93b253ac-baf5-4029-b800-7f6b53f5ede5)
![image](https://github.com/user-attachments/assets/8195b5a7-bf7e-4823-a77f-6f007da65e18)
![image](https://github.com/user-attachments/assets/7ab424b5-16a4-4c23-b1f7-f19ef5076679)
![image](https://github.com/user-attachments/assets/f3491557-a7aa-44db-9fbd-b90d3ff83cdd)
![image](https://github.com/user-attachments/assets/b205df74-3586-454c-a0d3-8867f47747fe)
![image](https://github.com/user-attachments/assets/36d15b8c-830a-4b3b-9815-2236fbb70e6f)
![image](https://github.com/user-attachments/assets/dc04cddf-b7b4-4931-9f4a-0651cc692bf4)
![image](https://github.com/user-attachments/assets/b4bb127d-d60e-492a-bd9d-bf17292d3ee1)
![image](https://github.com/user-attachments/assets/7558688a-d919-4ab4-a514-9155d8e563c8)
![image](https://github.com/user-attachments/assets/7af68f8a-d37b-4ae4-bb28-9e5caffea0ef)
![image](https://github.com/user-attachments/assets/2b04505b-a14a-4c2a-9678-1f968fad40d7)
![image](https://github.com/user-attachments/assets/d82b5fd1-9663-407d-9edd-120672de2957)










