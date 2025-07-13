# Welcome to your new notebook
# Type here in the cell editor to add code!
from pyspark.sql.functions import col, from_json ,split,to_date,to_timestamp,concat,lit
from pyspark.sql.types import IntegerType, DoubleType, DecimalType
from pyspark.sql import SparkSession

kafka_options = {
    "kafka.bootstrap.servers": "pkc-xrnwx.asia-south2.gcp.confluent.cloud:9092",
    "kafka.sasl.mechanism": "PLAIN",
    "kafka.security.protocol": "SASL_SSL",
    "kafka.sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username='username' password='password';",
    "subscribe": "Earthquakes",
    "startingOffsets": "earliest" 
}

spark = SparkSession.builder.appName("realtimeEarthquakes").getOrCreate()

streaming_df = (spark.readStream
  .format("kafka")
  .options(**kafka_options)
  .load()
)
processed_stream = streaming_df.selectExpr(
    "CAST(key AS STRING) AS key", 
    "CAST(value AS STRING) AS value"
)
df_with_array = processed_stream.withColumn("values_array", split(col("value"),"\\|"))
df_extracted = df_with_array.withColumn("location", col("values_array")[0]) \
                            .withColumn("magnitude", col("values_array")[1].cast(DoubleType())) \
                            .withColumn("longitude", col("values_array")[2].cast(DoubleType())) \
                            .withColumn("latitude", col("values_array")[3].cast(DoubleType())) \
                            .withColumn("date", to_date(col("values_array")[4], "yyyy-MM-dd")) \
                            .withColumn("time", to_timestamp(concat(col("values_array")[4],lit(" "),col("values_array")[5]),"yyyy-MM-dd HH:mm:ss.SSSSSS")) \

deduplicated_df = (df_extracted
    .withWatermark("time", "1440 minutes")  # Step 1: Define watermark. Allows for events to be up to 10 minutes late.
    .dropDuplicatesWithinWatermark(["key"]) # Step 2: Drop duplicates based on the unique 'eventId' within the watermark window.
)

query = (deduplicated_df
    .writeStream
    .format("delta")
    .option("checkpointLocation","Files/checkpoints")
    .outputMode("append")
    .trigger(availableNow=True)
    .toTable("Realtime_Earthquakes")
)

query.awaitTermination()
