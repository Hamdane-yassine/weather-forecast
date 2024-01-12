const { Kafka, Partitioners } = require("kafkajs");
const config = require('./config');

class KafkaConfig {
  constructor() {
    this.kafka = new Kafka({
      clientId: "nodejs-kafka",
      brokers: [`${config.kafka.kafkaBootstrapServers}`],
      createPartitioner: Partitioners.LegacyPartitioner
    });

    this.kafka.admin().connect().then(() => {
      console.log("Kafka admin connected");
      // Check if the topic exists, otherwise create it
      this.kafka.admin().listTopics().then((topics) => {
        if (!topics.includes("response")) {
          this.kafka.admin().createTopics({
            topics: [{
              topic: "response",
              numPartitions: parseInt(config.kafka.kafkaNumPartitions),
              replicationFactor: 1
            }]
          }).then(() => {
            this.kafka.admin().fetchTopicMetadata({ topics: ["response"] }).then((data) => {
              this.kafka.admin().createPartitions({
                topicPartitions: [{
                  topic: "response",
                  count: data.topics[0].partitions.length === 1 ? data.topics[0].partitions.length + parseInt(config.kafka.kafkaNumPartitions) - 1 : data.topics[0].partitions.length + parseInt(config.kafka.kafkaNumPartitions)
                }]
              }).then(() => console.log(`Created "response" topic with ${config.kafka.kafkaNumPartitions} partitions`));
            });
          });
        } else {
          console.log(`Kafka topic "response" already exists`);
          // Get number of partitions
          this.kafka.admin().fetchTopicMetadata({ topics: ["response"] }).then((data) => {
            this.kafka.admin().createPartitions({
              topicPartitions: [{
                topic: "response",
                count: data.topics[0].partitions.length === 1 ? data.topics[0].partitions.length + parseInt(config.kafka.kafkaNumPartitions) - 1 : data.topics[0].partitions.length + parseInt(config.kafka.kafkaNumPartitions)
              }]
            }).then(() => console.log(`Added ${config.kafka.kafkaNumPartitions} partitions to "response" topic`));
          });
        }
      });
    });

    this.producer = this.kafka.producer();
    this.consumer = this.kafka.consumer({ groupId: 'backend' });
  }

  async connectProducer() {
    try {
      await this.producer.connect();
      console.log('Kafka producer connected');
    } catch (error) {
      console.error('Failed to connect the producer:', error);
    }
  }

  async produce(topic, messages) {
    try {
      await this.producer.send({ topic, messages });
    } catch (error) {
      console.error("Error in Kafka producer:", error);
    }
  }

  async connectSubscribeAndRunConsumer(topic, callback) {
    try {
      await this.consumer.connect();
      console.log('Kafka consumer connected');
      await this.consumer.subscribe({ topic: topic, fromBeginning: false });
      console.log(`Kafka consumer subscribed to "${topic}" topic`);
      await this.consumer.run({
        eachMessage: async ({ message }) => {
          const value = message.value.toString();
          callback(value);
        },
      });
    } catch (error) {
      console.error('Failed to connect:', error);
    }
  }

}

module.exports = KafkaConfig;