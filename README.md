# FunDashboard
A fun dashboard by Django &amp; React &amp; Kafka
### Main Page
![Image description](./main.png)
### Customer Page
![Image description](./create_customer.png)
![Image description](./check_customer.png)
### Product Page
![Image description](./products.png)
### Bus Map Page
![Image description](./bus_map.png)

### Kafka Setup
Running the following commands under where Kafka was installed
##### Zookeeper
```
bin/zookeeper-server-start.sh config/zookeeper.properties
```
##### Kafka Server
```
bin/kafka-server-start.sh config/server.properties
```
### Real-time Bus Data Generator
```
python bus_data1.py
python bus_data2.py
```
### Endpoint
`/bus/data/`
