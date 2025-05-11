import logging

from visit_scheduler.package_utils.settings import VisitSchedulerSettings

settings = VisitSchedulerSettings()

level = settings.LOG_LEVEL
# create logger
logger = logging.getLogger("visit_scheduler")
logger.setLevel(level)

ch = logging.StreamHandler()
ch.setLevel(level)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

ch.setFormatter(formatter)

logger.addHandler(ch)
