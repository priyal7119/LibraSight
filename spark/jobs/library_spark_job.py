from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    count,
    sum,
    avg,
    year,
    month
)


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "library_clean.parquet"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "spark"
    / "output"
)


# --------------------------------------------------
# 2. Write DataFrame to Parquet
# --------------------------------------------------

def write_dataframe_to_parquet(
    df,
    output_dir: Path
) -> None:

    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    if hasattr(df, "toPandas"):
        pandas_df = df.toPandas()
    else:
        pandas_df = df

    parquet_file = (
        output_dir
        / "part-00000.parquet"
    )

    pandas_df.to_parquet(
        parquet_file,
        index=False
    )


# --------------------------------------------------
# 3. Main Spark processing function
# --------------------------------------------------

def run_spark_processing():

    print("=" * 60)
    print("LIBRASIGHT - PYSPARK PROCESSING")
    print("=" * 60)

    # --------------------------------------------------
    # Create Spark Session
    # --------------------------------------------------

    spark = (
        SparkSession.builder
        .appName("LibraSightLibraryAnalytics")
        .master("local[*]")
        .config(
            "spark.hadoop.fs.permissions.umask-mode",
            "022"
        )
        .config(
            "spark.hadoop.fs.file.impl",
            "org.apache.hadoop.fs.LocalFileSystem"
        )
        .getOrCreate()
    )

    try:

        # --------------------------------------------------
        # Read Parquet
        # --------------------------------------------------

        print("\nReading cleaned Parquet data...")

        if not INPUT_FILE.exists():
            raise FileNotFoundError(
                f"Input Parquet file not found: {INPUT_FILE}"
            )

        df = spark.read.parquet(
            str(INPUT_FILE)
        )

        print("Parquet loaded successfully.")

        # --------------------------------------------------
        # Display schema
        # --------------------------------------------------

        print("\nSpark DataFrame Schema:")

        df.printSchema()

        # --------------------------------------------------
        # Display record count
        # --------------------------------------------------

        total_records = df.count()

        print(
            f"\nTotal records: {total_records}"
        )

        # --------------------------------------------------
        # Display sample records
        # --------------------------------------------------

        print("\nSample records:")

        df.show(
            5,
            truncate=False
        )

        # --------------------------------------------------
        # BOOK ANALYTICS
        # --------------------------------------------------

        print("\n--- Book Analytics ---")

        book_analytics = (
            df.groupBy(
                "book_id",
                "book_title",
                "author"
            )
            .agg(
                count("transaction_id").alias(
                    "booking_count"
                ),
                sum("fine_amount").alias(
                    "total_fine"
                ),
                avg("renewal_count").alias(
                    "average_renewals"
                )
            )
        )

        book_analytics.orderBy(
            "booking_count",
            ascending=False
        ).show(
            10,
            truncate=False
        )

        # --------------------------------------------------
        # GENRE ANALYTICS
        # --------------------------------------------------

        print("\n--- Genre Analytics ---")

        genre_analytics = (
            df.groupBy("genre")
            .agg(
                count("transaction_id").alias(
                    "transaction_count"
                ),
                avg("fine_amount").alias(
                    "average_fine"
                )
            )
        )

        genre_analytics.orderBy(
            "transaction_count",
            ascending=False
        ).show(
            truncate=False
        )

        # --------------------------------------------------
        # READER ANALYTICS
        # --------------------------------------------------

        print("\n--- Reader Analytics ---")

        reader_analytics = (
            df.groupBy("reader_type")
            .agg(
                count("transaction_id").alias(
                    "transaction_count"
                ),
                avg("renewal_count").alias(
                    "average_renewals"
                )
            )
        )

        reader_analytics.orderBy(
            "transaction_count",
            ascending=False
        ).show(
            truncate=False
        )

        # --------------------------------------------------
        # BRANCH ANALYTICS
        # --------------------------------------------------

        print("\n--- Branch Analytics ---")

        branch_analytics = (
            df.groupBy(
                "branch_id",
                "branch_name",
                "city"
            )
            .agg(
                count("transaction_id").alias(
                    "transaction_count"
                ),
                sum("fine_amount").alias(
                    "total_fine"
                )
            )
        )

        branch_analytics.orderBy(
            "transaction_count",
            ascending=False
        ).show(
            10,
            truncate=False
        )

        # --------------------------------------------------
        # COLLECTION ANALYTICS
        # --------------------------------------------------

        print("\n--- Collection Analytics ---")

        collection_analytics = (
            df.groupBy(
                "collection_status"
            )
            .agg(
                count("book_id").alias(
                    "book_transaction_count"
                ),
                avg("available_copies").alias(
                    "average_available_copies"
                )
            )
        )

        collection_analytics.show(
            truncate=False
        )

        # --------------------------------------------------
        # YEARLY TRENDS
        # --------------------------------------------------

        print("\n--- Yearly Reading Trends ---")

        yearly_trends = (
            df.groupBy(
                year("checkout_date").alias(
                    "checkout_year"
                )
            )
            .agg(
                count("transaction_id").alias(
                    "transaction_count"
                )
            )
            .orderBy(
                "checkout_year"
            )
        )

        yearly_trends.show()

        # --------------------------------------------------
        # MONTHLY TRENDS
        # --------------------------------------------------

        print("\n--- Monthly Reading Trends ---")

        monthly_trends = (
            df.groupBy(
                year("checkout_date").alias(
                    "checkout_year"
                ),
                month("checkout_date").alias(
                    "checkout_month"
                )
            )
            .agg(
                count("transaction_id").alias(
                    "transaction_count"
                )
            )
            .orderBy(
                "checkout_year",
                "checkout_month"
            )
        )

        monthly_trends.show(
            truncate=False
        )

        # --------------------------------------------------
        # TRANSACTION STATUS ANALYTICS
        # --------------------------------------------------

        print(
            "\n--- Transaction Status Analytics ---"
        )

        status_analytics = (
            df.groupBy(
                "transaction_status"
            )
            .agg(
                count("transaction_id").alias(
                    "transaction_count"
                ),
                avg("fine_amount").alias(
                    "average_fine"
                )
            )
        )

        status_analytics.show(
            truncate=False
        )

        # --------------------------------------------------
        # Save analytical datasets
        # --------------------------------------------------

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        write_dataframe_to_parquet(
            book_analytics,
            OUTPUT_DIR / "book_analytics"
        )

        write_dataframe_to_parquet(
            genre_analytics,
            OUTPUT_DIR / "genre_analytics"
        )

        write_dataframe_to_parquet(
            reader_analytics,
            OUTPUT_DIR / "reader_analytics"
        )

        write_dataframe_to_parquet(
            branch_analytics,
            OUTPUT_DIR / "branch_analytics"
        )

        write_dataframe_to_parquet(
            collection_analytics,
            OUTPUT_DIR / "collection_analytics"
        )

        write_dataframe_to_parquet(
            yearly_trends,
            OUTPUT_DIR / "yearly_trends"
        )

        write_dataframe_to_parquet(
            monthly_trends,
            OUTPUT_DIR / "monthly_trends"
        )

        write_dataframe_to_parquet(
            status_analytics,
            OUTPUT_DIR / "status_analytics"
        )

        print(
            "\nAnalytical datasets saved successfully."
        )

        print(
            f"\nOutput directory:\n{OUTPUT_DIR}"
        )

        print("\n" + "=" * 60)
        print("PYSPARK PROCESSING COMPLETED SUCCESSFULLY")
        print("=" * 60)

        return True

    finally:

        # --------------------------------------------------
        # Stop Spark
        # --------------------------------------------------

        spark.stop()

        print("\nSpark session stopped.")


# --------------------------------------------------
# 4. Run directly
# --------------------------------------------------

if __name__ == "__main__":
    run_spark_processing()