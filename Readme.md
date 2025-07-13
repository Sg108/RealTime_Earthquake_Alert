# **Real-Time Earthquake Monitoring & Alerting Pipeline**

**A near real-time data pipeline that ingests earthquake data from the USGS, processes it using Kafka and Microsoft Fabric, and provides BI reports and critical magnitude alerts.**

## **📋 Table of Contents**

* [Overview](https://www.google.com/search?q=%23-overview)  
* [System Architecture](https://www.google.com/search?q=%23-system-architecture)  
* [Data Flow](https://www.google.com/search?q=%23-data-flow)  
* [Components](https://www.google.com/search?q=%23-components)  
  * [1\. Data Source](https://www.google.com/search?q=%231-data-source)  
  * [2\. Data Producer (AWS EC2)](https://www.google.com/search?q=%232-data-producer-aws-ec2)  
  * [3\. Messaging Queue (Confluent Kafka)](https://www.google.com/search?q=%233-messaging-queue-confluent-kafka)  
  * [4\. Consumer & Processor (Microsoft Fabric)](https://www.google.com/search?q=%234-consumer--processor-microsoft-fabric)  
  * [5\. Reporting (Power BI)](https://www.google.com/search?q=%235-reporting-power-bi)  
  * [6\. Alerting System](https://www.google.com/search?q=%236-alerting-system)  
* [Setup & Deployment](https://www.google.com/search?q=%23-setup--deployment)  
* [Future Enhancements](https://www.google.com/search?q=%23-future-enhancements)

## **🔭 Overview**

This project implements an end-to-end data engineering solution to monitor global earthquake activity in near real-time. The pipeline is designed to be robust, scalable, and automated.

Every five minutes, it fetches the latest earthquake data from the U.S. Geological Survey (USGS), streams it through a Kafka topic, processes it using a Spark job in Microsoft Fabric, and visualizes the results in a Power BI dashboard. A crucial feature of this system is its automated alerting mechanism, which sends an email notification for any seismic event with a magnitude greater than 6.0.

## **🏗️ System Architecture**

The architecture is designed to decouple data ingestion from data processing, ensuring resilience and scalability.

graph TD  
    subgraph "Data Source"  
        A\[USGS Earthquake API\]  
    end

    subgraph "Producer on AWS"  
        B(AWS EC2 Instance) \-- Fetches data every 5 mins \--\> A  
        B \-- Runs Python Producer Script \--\> C\[Confluent Kafka\]  
    end

    subgraph "Messaging Queue"  
        C \-- Topic: 'Earthquakes' \--\> D  
    end

    subgraph "Processing & Analytics in Microsoft Fabric"  
        D(Spark Job Definition) \-- Consumes from Kafka every 5 mins \--\> C  
        D \-- Processes & Cleans Data \--\> E\[Lakehouse Table\]  
        E \-- Powers \--\> F\[Power BI Report\]  
        D \-- Checks magnitude \> 6 \--\> G{Alerting Logic}  
    end

    subgraph "Outputs"  
        F  
        G \-- Sends Email \--\> H\[\<i class='fa fa-envelope'\>\</i\> Email Alert\]  
    end

    style A fill:\#f9f,stroke:\#333,stroke-width:2px  
    style B fill:\#FF9900,stroke:\#333,stroke-width:2px  
    style C fill:\#231F20,stroke:\#fff,stroke-width:2px,color:\#fff  
    style D fill:\#7FBA00,stroke:\#333,stroke-width:2px  
    style E fill:\#01B8AA,stroke:\#333,stroke-width:2px  
    style F fill:\#F2C811,stroke:\#333,stroke-width:2px  
    style H fill:\#E83B3B,stroke:\#333,stroke-width:2px

## **🌊 Data Flow**

1. **Fetch Data:** A Python script, running on an AWS EC2 instance and scheduled via a cron job, makes an API call to the USGS FDSN Event Web Service every five minutes to retrieve data on recent earthquakes.  
2. **Produce to Kafka:** The script acts as a Kafka producer, sending the raw JSON data of each earthquake event as a separate message to the Earthquakes topic in a Confluent Kafka cluster.  
3. **Consume from Kafka:** A Spark Job Definition in Microsoft Fabric runs on a five-minute schedule. It connects to the Kafka topic and pulls the latest batch of messages that have arrived since its last run.  
4. **Process and Store:** The Spark job parses the JSON messages, flattens the structure, cleans the data, and appends the new records to a Delta table in a Microsoft Fabric Lakehouse.  
5. **Check for Alerts:** During processing, the Spark job checks the magnitude of each event. If any event has a magnitude greater than 6.0, it triggers an alerting function.  
6. **Send Alert:** The alerting function sends a formatted email to a predefined list of recipients, containing details about the high-magnitude earthquake.  
7. **Visualize Data:** The Delta table in the Lakehouse acts as the source for a Power BI report. The report is set to auto-refresh, providing an interactive and up-to-date dashboard of global earthquake activity.

## **🧩 Components**

### **1\. Data Source**

* **Service:** [USGS FDSN Event Web Service](https://earthquake.usgs.gov/fdsnws/event/1/)  
* **Endpoint:** https://earthquake.usgs.gov/fdsnws/event/1/query  
* **Details:** This API provides real-time earthquake data in various formats. We query it for events that occurred in the last 5 minutes to avoid duplicate processing.

### **2\. Data Producer (AWS EC2)**

* **Infrastructure:** AWS EC2 Instance (e.g., t2.micro).  
* **Logic:** A Python script (producer.py) using the requests library to fetch data and the confluent-kafka library to send it to Kafka.  
  \*/5 \* \* \* \* /usr/bin/python3 /path/to/producer.py

### **3\. Messaging Queue (Confluent Kafka)**

* **Platform:** Confluent Cloud or a self-hosted Kafka cluster.  
* **Topic:** Earthquakes  
* **Purpose:** Acts as a durable and scalable buffer between the data producer and the consumer, ensuring data is not lost if the consumer is temporarily unavailable.

### **4\. Consumer & Processor (Microsoft Fabric)**

* **Component:** Spark Job Definition  
* **Language:** PySpark  
* **Logic:**  
  * Establishes a connection to the Kafka topic.  
  * Uses Structured Streaming to read the latest data (readStream).  
  * Parses JSON, selects required fields (id, magnitude, place, time, tsunami, geometry, etc.).  
  * Appends the processed micro-batch to a Delta table in a Fabric Lakehouse.  
  * Implements the alerting logic to check for high-magnitude events.  
* **Scheduling:** Scheduled to run every 5 minutes within the Fabric workspace.

### **5\. Reporting (Power BI)**

* **Source:** The Delta table created by the Spark job in the Fabric Lakehouse.  
* **Features:**  
  * A world map visualizing earthquake locations.  
  * Slicers to filter by magnitude, time. 
  * A table showing details of the most recent events.

### **6\. Alerting System**

* **Trigger:** A condition in the Spark job (magnitude \> 6.0).  
* **Action:** Uses Python's smtplib library or a third-party email API to send a notification.  
* **Content:** The email includes critical information like the earthquake's location, magnitude, time, and a link to the USGS event page.

## **🛠️ Setup & Deployment**

1. **AWS EC2 Producer:**  
   * Launch an EC2 instance.  
   * Install Python and the required libraries: pip install requests confluent-kafka.  
   * Place the producer.py script on the instance.  
   * Ensure network rules allow outbound traffic to the Confluent Kafka cluster.  
2. **Confluent Kafka:**  
   * Create a Kafka cluster and get the bootstrap server URL and API keys.  
   * Create the Earthquakes topic.  
3. **Microsoft Fabric:**  
   * Create a Lakehouse to store the final data.  
   * Create a new Spark Job Definition and upload your PySpark consumer script.  
   * Securely store Kafka and email credentials using a Fabric-supported secret management solution.  
   * Configure the job's schedule to run every 5 minutes.  
4. **Power BI:**  
   * Open Power BI Desktop and connect to the Fabric Lakehouse.  
   * Select the earthquakes Delta table as the data source.  
   * Build your report and publish it to the Fabric workspace.  
   * Configure scheduled refresh for the semantic model.

