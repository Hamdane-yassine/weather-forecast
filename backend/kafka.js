const { Kafka, Partitioners } = require("kafkajs");

class KafkaConfig {
  constructor() {
    this.kafka = new Kafka({
      clientId: "nodejs-kafka",
      brokers: ["localhost:9092"],
      createPartitioner: Partitioners.LegacyPartitioner
    });
    this.producer = this.kafka.producer();
  }

  async produce(topic, messages) {
    try {
      await this.producer.connect();
      await this.producer.send({ topic, messages });
    } catch (error) {
      console.error("Error in Kafka producer:", error);
    } finally {
      await this.producer.disconnect();
    }
  }
}

module.exports = KafkaConfig;