from src.core.dependencies import get_app_config
from src.core.logging import get_dict_config

bind = "0.0.0.0:8000"
forwarded_allow_ips = "*"

worker_class = "uvicorn.workers.UvicornWorker"
workers = 5

worker_tmp_dir = "/dev/shm"  # noqa: S108 (insecure usage of temporary file)

logconfig_dict = get_dict_config(app_config=get_app_config())
