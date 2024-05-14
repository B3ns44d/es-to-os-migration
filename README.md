# Elasticsearch to OpenSearch Migration Script

This Python script facilitates the migration of data from a remote Elasticsearch cluster to an OpenSearch cluster using
the Reindex API. It is designed to handle indices individually, allowing for a more manageable error recovery process
and the potential for parallel execution.

## Features

- Migrates specified indices from a remote Elasticsearch cluster to a single index in an OpenSearch cluster.
- Utilizes the Reindex API with asynchronous task handling to improve efficiency.
- Periodically checks the status of each reindexing task, ensuring successful completion and error handling.
- Highly configurable through a YAML file, enabling easy adjustments for different source and target clusters or
  indices.
- Detailed logging provides insight into the migration process, task statuses, and any encountered errors.

## Prerequisites

Before running the script, ensure you have the following prerequisites installed:

- Python 3.6 or later
- `opensearch-py` package
- `pyyaml` package

You can install the required packages using pip:

```bash
pip install opensearch-py pyyaml
```

## Configuration

Modify the `config.yml` file to specify the source indices, target index, and both the source and target cluster
configurations. Here is an example structure for the `config.yml`:

```yaml
source_indices:
  - index1
  - index2
  - index3
target_index: target_index
es_target_config:
  hosts: [ 'http://target_opensearch:9200' ]
  http_auth: [ 'user', 'password' ]
  use_ssl: True
  verify_certs: False
  ssl_assert_hostname: False
  ssl_show_warn: False
es_source_remote:
  host: 'http://source_elasticsearch:9200'
  username: 'source_user'
  password: 'source_password'
```

## Usage

Run the script from the command line, specifying the path to your configuration file using the `--config` flag:

```bash
python migrate_indices.py --config /path/to/your/config.yml
```

## Logging

The script uses Python's built-in `logging` module to log information about the migration process, including start
times, end times, task statuses, and errors. Logs are printed to the console for real-time monitoring.
