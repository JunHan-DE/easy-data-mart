create_stream_sql = """
CREATE STREAM {topic} ({column_info})
  WITH (kafka_topic='{topic}', value_format='json', partitions=1);
"""
