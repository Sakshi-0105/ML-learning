from pyspark.sql import SparkSession

# Create Spark Session
spark = SparkSession.builder \
    .appName("MyFirstApp") \
    .getOrCreate()

# Create a simple DataFrame
data = [("Sakshi", 24), ("Tanvi", 25), ("Ravi", 30)]
df = spark.createDataFrame(data, ["Name", "Age"])

df.show()

# Stop Spark session
spark.stop()
