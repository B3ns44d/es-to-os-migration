import yaml
import logging
import time
import argparse
from datetime import datetime
from typing import Dict, Optional
from opensearchpy import OpenSearch as OpenSearchTarget

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(file_path: str) -> Dict[str, any]:
    """Load configuration from a YAML file."""
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        logging.info(f"Loaded configuration from {file_path}")
        return config
    except Exception as e:
        logging.error(f"Failed to load configuration from {file_path}. Error: {e}")
        raise

def initialize_opensearch_client(config: Dict[str, any]) -> OpenSearchTarget:
    """Initialize and return an OpenSearch client based on provided config."""
    try:
        es_target = OpenSearchTarget(**config['es_target_config'])
        logging.info(f"Initialized OpenSearch client for target cluster at {config['es_target_config']['hosts']}")
        return es_target
    except Exception as e:
        logging.error(f"Failed to initialize OpenSearch client. Error: {e}")
        raise

def start_reindex_task(es_target: OpenSearchTarget, source_index: str, target_index: str,
                       source_remote: Dict[str, str]) -> Optional[str]:
    """Start a reindex task from source index to target index, including remote source."""
    logging.info(f"Attempting to start reindex from {source_index} on remote {source_remote['host']} to {target_index} on target cluster")
    body = {
        "source": {
            "remote": {
                "host": source_remote['host'],
                "username": source_remote['username'],
                "password": source_remote['password']
            },
            "index": source_index
        },
        "dest": {
            "index": target_index
        }
    }
    try:
        response = es_target.reindex(body=body, wait_for_completion=False, params={"requests_per_second": "-1"})
        task_id = response['task']
        logging.info(f"Reindex task started successfully. Source: {source_index}, Target: {target_index}, Task ID: {task_id}")
        return task_id
    except Exception as e:
        logging.error(f"Failed to start reindex task for {source_index}. Error: {e}")
        return None

def check_task_status(es_target: OpenSearchTarget, task_id: str) -> Dict:
    """Check the status of a reindex task."""
    try:
        response = es_target.tasks.get(task_id=task_id)
        logging.info(f"Checked status for task {task_id}: {'completed' if response.get('completed', False) else 'in progress'}")
        return response
    except Exception as e:
        logging.error(f"Failed to check status for task {task_id}. Error: {e}")
        return {"completed": True, "error": str(e)}

def migrate_indices(config_path: str):
    """Main function to orchestrate the migration based on the provided YAML configuration."""
    start_time = datetime.now()
    try:
        config = load_config(config_path)
        es_target = initialize_opensearch_client(config)
        task_ids = {}

        for index in config['source_indices']:
            task_id = start_reindex_task(es_target, index, config['target_index'], config['es_source_remote'])
            if task_id:
                task_ids[index] = task_id

        while task_ids:
            time.sleep(10)  # Check status every 10 seconds
            for index, task_id in list(task_ids.items()):
                status = check_task_status(es_target, task_id)
                if status['completed']:
                    if 'error' in status:
                        logging.error(f"Reindexing task for {index} failed. Error: {status['error']}")
                    else:
                        logging.info(f"Reindexing task for {index} completed successfully.")
                    task_ids.pop(index)
                else:
                    logging.info(f"Reindexing task for {index} is still in progress...")

        logging.info(f"Migration completed in {(datetime.now() - start_time).total_seconds()} seconds.")
    except Exception as e:
        logging.error(f"Migration failed. Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate indices from Elasticsearch to OpenSearch.')
    parser.add_argument('--config', help='Path to the configuration YAML file.', required=True)
    args = parser.parse_args()

    migrate_indices(args.config)
