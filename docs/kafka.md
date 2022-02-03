# Kafka

[Apache Kafka](https://kafka.apache.org/) will be used to maintain alarm state messages, alarm hierarchy configuration, and for the communication of commands between the client and alarm server.  

Kafka uses a publish/subscribe model to synchronize state between data producers and data ingestors. Messages are constructed using a key-value structure. Producers write events to Kafka servers (brokers) using categorized messages termed topics. Topic messages are divided into a designated number of bucketed partitions, defined using the message keys. These partitions are replicated across brokers, with one replica elected as the leader responsible for the reading/writing of a topic. In the case of leader broker failure, a replica becomes leader. Leaders write new messages to other replicas and reads/writes are consequently parallelized across the cluster.  

Kafka brokers are synchronized by a Zookeeper node. This Zookeeper node is responsible for leader election, maintaining a registry of cluster members, configuring topics (number of partitions, leader location, etc.), and access control. We will use the Zookeeper packaged with the Kafka distribution until its deprecation. The Kafka broker configuration file assigns an id for the broker, communication protocols, partition count, compaction settings and others.  

The latest Kafka version as of writing (2.8.1) will be used out of the box, with configuration options tailored to frequent log compaction for state maintenance. The release of [Kafka Improvement Proposal 500](https://cwiki.apache.org/confluence/display/KAFKA/KIP-500%3A+Replace+ZooKeeper+with+a+Self-Managed+Metadata+Quorum) at some point in 2021 warrants version reconsideration, as the new deprecation of zookeeper will allow the removal of the dedicated server and move to a self managed quorum model.

The NALMS production Kafka cluster consists of three nodes, topic deletion enabled, with compaction cleanup policy for state messages and deletion for configuration and commands and frequent cleanup operations (max lag 1s). A development cluster consists of only a single node, hosted locally. A full description of configuration options is provided in the Apache Kafka [documentation](https://kafka.apache.org/documentation/#brokerconfigs).

Each broker may be configured with a keystore and truststore for [SSL](networking.md) authentication and encryption. 

## Kafka messages

Categorized Kafka messages facilitate all interactions with the alarm server. Alarm events are translated into Kafka messages by the alarm server (state topic), commands are communicated to the alarm server (command topic), and configurations are defined and manipulated (config topic). The key-value structure of the Kafka messages maintains the alarm hierarchy. Keys are prefixed with “command”, “state”, or “config”, and represent the full alarm item path as forward slash delineated locations in the hierarchy. 

For example, KLYS:LI23:21:DL_WG_TEMP in the following tree would be indicated by the path: /Temp/KLYS/KLYS:LI23:21/KLYS:LI23:21:DL_WG_TEMP.

```
Temp  
└── KLYS  
    ├── KLYS:LI23:11  
    │   └── KLYS:LI23:11:DL_WG_TEMP  
    ├── KLYS:LI23:21  
    │   └── KLYS:LI23:21:DL_WG_TEMP  
    ├── KLYS:LI23:31  
    │   └── KLYS:LI23:31:DL_WG_TEMP  
    ├── KLYS:LI23:41  
    │   └── KLYS:LI23:41:DL_WG_TEMP  
    ├── KLYS:LI23:51
    │   └── KLYS:LI23:51:DL_WG_TEMP
    ├── KLYS:LI23:61
    │   └── KLYS:LI23:61:DL_WG_TEMP
    ├── KLYS:LI23:71
    │   └── KLYS:LI23:71:DL_WG_TEMP
    └── KLYS:LI23:81
        └── KLYS:LI23:81:DL_WG_TEMP

```

The Kafka configuration message for the PV would be keyed by the string `config:/Temp/KLYS/KLYS:LI23:11/KLYS:LI23:11:DL_WG`. Associated values are JSON representations of the associated values. Representations for alarm tree leaves and nodes are outlined below. Undefined elements are omitted in practice.

### Alarm leaf configuration


```json
{
    "user":        String,
    "host":        String,
    "description": String,
    "delay":       Integer,
    "count":       Integer,
    "filter":      String,
    "guidance": [{"title": String, "details": String}],
    "displays": [{"title": String, "details": String}],
    "commands": [{"title": String, "details": String}],
    "actions":  [{"title": String, "details": String}]
}
```

## Alarm node configuration

```json
{
    "user":        String,
    "host":        String,
    "guidance": [{"title": String, "details": String}],
    "displays": [{"title": String, "details": String}],
    "commands": [{"title": String, "details": String}],
    "actions":  [{"title": String, "details": String}]
}
```

### Alarm leaf state 
```json
{
    "severity": String,
    "latch": Boolean,
    "message":  String,
    "value":    String,
    "time": {
                "seconds": Long,
                "nano":    Long
            },
    "current_severity": String,
    "current_message":  String,
    "mode":     String,
}
```

### Alarm node state
```json
{
    "severity": String,
    "mode":     String,
}
```

### Command

```json
{
    "user":    String,
    "host":    String,
    "command": String
}
```
