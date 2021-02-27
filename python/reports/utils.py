import shotgun_api3
import logging
import csv

from constants import ReportConstants


def get_logger():
    """
    Get a python logging object
        Logs debug or higher to log file
        Logs info or higher to console

    Returns: logger_main, logger_shot, logger_asset
        python logging logger objects

    """
    # setting up file logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        filename="D:\code\logs\sg_report.log",
        filemode="w"
    )

    # Setting up console logging.
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)-12s %(levelname)-8s %(message)s")
    console.setFormatter(formatter)

    # Adding console handler
    logging.getLogger("").addHandler(console)

    # Generating name of each module's logger
    logger_main = logging.getLogger("sg_report")
    logger_shot = logging.getLogger("sg_report.shot_report")
    logger_asset = logging.getLogger("sg_report.asset_report")

    return logger_main, logger_shot, logger_asset


def get_sg_connection():
    """

    Returns: Shotgun_api3 Shotgun object

    """
    sg = shotgun_api3.Shotgun(
        base_url=ReportConstants.shotgun_url,       # Website url. Eg. "https://dreamworks.shotgunstudio.com"
        script_name=ReportConstants.login,          # Scrip user
        api_key=ReportConstants.password,           # Script key
    )
    return sg


def get_sg_project_from_id(sg, project_id):
    """
    Gets shotgun project entity from the given entity ID.

    Args:
        sg: Shotgun_api3 Shotgun object
        project_id(int): Shotgun project entity ID

    Returns: Shotgun project dictionary

    """
    filter_ = [
        ["id", "is", project_id]
    ]
    fields = ["name"]
    return sg.find_one("Project", filter_, fields)


def get_shot_tasks(sg, sg_project):
    """

    Args:
        sg: Shotgun_api3 Shotgun object
        sg_project(dict): Shotgun project entity dictionary

    Returns: All Shotgun shot tasks linked to the given shotgun project.

    """
    filter_ = [
        ["project", "is", sg_project],
        ["entity", "type_is", "Shot"],
    ]

    return sg.find("Task", filter_, ReportConstants.shot_task_fields)


def write_csv(path, field_template, csv_dict):
    """

    Args:
        path(str): Location to copy file to. Must include filename and extension.
        field_template(list): List of column names for final csv data.
        csv_dict(list of dict): List of formatted task dictionaries where keys match the field template key names.

    Returns: Writes a csv of the given data to the given location.

    """
    with open(path, "w") as csv_file:
        writer = csv.DictWriter(csv_file, lineterminator="\n", fieldnames=field_template)
        writer.writeheader()
        writer.writerows(csv_dict)
