from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder \
    .appName("LibraSightTest") \
    .master("local[*]") \
    .getOrCreate()

print("Spark session started successfully!")

# Create a small test DataFrame
data = [
    (1, "Book A"),
    (2, "Book B"),
    (3, "Book C")
]

columns = ["book_id", "book_name"]

df = spark.createDataFrame(data, columns)

# Display DataFrame
df.show()

# Stop Spark
spark.stop()

print("Spark session stopped successfully!")