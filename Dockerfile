FROM apache/airflow:3.3.1

USER root

# Install Java required by PySpark
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow

# Install LibraSight Python dependencies
RUN pip install --no-cache-dir \
    pyspark==4.2.0 \
    pandas \
    pyarrow \
    psycopg2-binary