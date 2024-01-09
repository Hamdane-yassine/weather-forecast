const { Kafka, Partitioners } = require("kafkajs");

class KafkaConfig {
  constructor() {
    this.kafka = new Kafka({
      clientId: "nodejs-kafka",
      brokers: ["localhost:9092"],
      createPartitioner: Partitioners.LegacyPartitioner
    });
    this.producer = this.kafka.producer();
    this.consumer = this.kafka.consumer({ groupId: 'my-consumer-group' });
  }

  async connectProducer() {
    try {
      await this.producer.connect();
      console.log('Kafka producer connected');
    } catch (error) {
      console.error('Failed to connect the producer:', error);
    }
  }

  async connectAndSubscribeConsumer(topic) {
    try {
      await this.consumer.connect();
      console.log('Kafka consumer connected');
      await this.consumer.subscribe({ topic: topic, fromBeginning: false });
      console.log(`Kafka consumer subscribed to "${topic}" topic`);
    } catch (error) {
      console.error('Failed to connect:', error);
    }
  }

  async produce(topic, messages) {
    try {
      await this.producer.send({ topic, messages });
    } catch (error) {
      console.error("Error in Kafka producer:", error);
    } finally {
      await this.producer.disconnect();
    }
  }

  async consume(callback) {
    try {
      await this.consumer.run({
        eachMessage: async ({ message }) => {
          const value = message.value.toString();
          callback(value);
        },
      });
    } catch (error) {
      console.error('Error in Kafka consumer:', error);
    }
  }
}

module.exports = KafkaConfig;