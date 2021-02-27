import argparse
import os
import sys
import pprint

from reports import utils
from constants import ReportConstants


def get_asset_report_dict(asset_tasks, prod_assets):
    """

    Args:
        asset_tasks(list of dict): List of shotgun task entity dictionaries
        prod_assets(set): set containing production asset names.

    Returns:

    """
    csv_tasks = []
    for task in asset_tasks:
        task_dict = {                                                                   # Example:
            ReportConstants.id: str(task["id"]),                                        # "ID": "1234"
            ReportConstants.task_name: task["content"],                                 # "Task Name": "surfaceRender"
            ReportConstants.step: task["step"].get("name", ""),                         # "Step": "surface"
            ReportConstants.task_status: task["sg_status_list"],                        # "Task Status": "ip"
            ReportConstants.asset_name: task[ReportConstants.task_asset_name],          # "Asset Name": "assetName"
            ReportConstants.asset_type: task[ReportConstants.task_asset_type],          # "Asset Type": "char"
            ReportConstants.start_date: task["start_date"],                             # "Start Date:" "2021-02-25"
            ReportConstants.due_date: task["due_date"],                                 # "Due Date": "2021-03-05"
            ReportConstants.prod_asset: (                                               # "Production Asset": "True"
                "True" if task[ReportConstants.task_asset_name] in prod_assets else "False"
            ),
            ReportConstants.tags: (                                                     # "Tags": "tag1, tag2, tag3"
                ", ".join(tag["name"] for tag in task["tags"])
            ),
        }
        csv_tasks.append(task_dict)

    return csv_tasks


def get_production_assets_from_shots(prod_shots, all_tasks):
    """

    Args:
        prod_shots(list f dict): List of Production shot entity dictionaries
        all_tasks(list of dict): All project asset task dictionaries

    Returns: Filtered list of production assets where the following is true:
                    The Asset's status is "in progress"
                    They are linked to a Production Shot via the Shots field

    """
    # Can add any logic here that is needed to validate production tasks.
    prod_assets = []
    for shot in prod_shots:
        # If no assets linked to shot, continue.
        if not shot["assets"]:
            continue
        # Names of any linked assets are appended.
        for asset in shot["assets"]:
            prod_assets.append(asset["name"])

    # Getting rid of duplicates
    prod_assets = set(prod_assets)

    fin_prod_assets = []
    for task in all_tasks:
        # If the asset status is not "ip", continue
        if not task[ReportConstants.task_asset_status] == "ip":
            continue
        # if the task has no linked asset name, continue
        if not task[ReportConstants.task_asset_name]:
            continue
        # If the tasks asset name is in the production assets list, add asset name to final list
        if task[ReportConstants.task_asset_name] in fin_prod_assets:
            continue
        if task[ReportConstants.task_asset_name] in prod_assets:
            fin_prod_assets.append(task[ReportConstants.task_asset_name])

    return set(fin_prod_assets)


def get_production_shots(sg, sg_project):
    """

    Args:
        sg: Shotgun_api3 Shotgun object
        sg_project(dict): Shotgun project entity dictionary

    Returns: list of shotgun Shot entitiy dictionaries if the following is true:
                    Shot status is "in progress"
                    Sequence status is "in progress"

    """
    filter_ = [
        ["project", "is", sg_project],
        ["sg_status_list", "is", "ip"],
        ["sg_sequence.Sequence.sg_status_list", "is", "ip"],
    ]
    fields = ["code", "sg_status_list", "sg_sequence.Sequence.sg_status_list", "assets"]
    return sg.find("Shot", filter_, fields)


def get_asset_tasks(sg, sg_project):
    """

    Args:
        sg: Shotgun_api3 Shotgun object
        sg_project(dict): Shotgun project entity dictionary

    Returns: All Shotgun asset tasks linked to the given shotgun project.

    """
    filter_ = [
        ["project", "is", sg_project],
        ["entity", "type_is", "Asset"],
    ]
    return sg.find("Task", filter_, ReportConstants.asset_task_fields)


def asset_run(args, logger):
    """

    Args:
        args: parser arguments
        logger: python logging logger object

    Returns: True if csv is written to the given location.
             False if not

    """
    logger.info("Starting Asset Report generation.")

    # Getting shotgun connection and shotgun project entity
    project_id = args.project_id
    sg = utils.get_sg_connection()
    sg_project = utils.get_sg_project_from_id(sg, project_id)

    # If tool can't find a shotgun project from the given ID, exit
    if not sg_project:
        logger.warning("Could not find project from the given ID. Exiting.")
        return False

    # Getting asset tasks
    # Note, this is often one of the most time consuming part of the process.
    logger.info("Getting all asset tasks for project {} from Shotgun.".format(sg_project["name"]))
    asset_tasks = get_asset_tasks(sg, sg_project)
    logger.info("Got {} asset tasks.".format(len(asset_tasks)))

    # Filtering list down to production assets
    # If asset is linked to a production shot, it is a production asset.
    prod_shots = get_production_shots(sg, sg_project)
    prod_assets = get_production_assets_from_shots(prod_shots, asset_tasks)
    logger.debug("Got {} production assets.".format(len(prod_assets)))

    # Processing tasks into final report format.
    logger.info("Compiling report.")
    report_dict = get_asset_report_dict(asset_tasks, prod_assets)

    logger.info("Writing report to csv")
    # csv will error if the path doesn't exist.
    dir_ = os.path.dirname(args.path)
    if not os.path.exists(dir_):
        logger.debug("Creating directory: \n{}".format(dir_))
        os.mkdir(dir_)

    # Writing out csv of report dictionary.
    utils.write_csv(args.path, ReportConstants.asset_csv_header_order, report_dict)
    return True


def get_parser():
    """

    Returns: Shot report module argument parser

    """
    parser = argparse.ArgumentParser(
        prog="asset_report",
        description="Generate a csv report for Shotgun Asset tasks.",
    )
    parser.add_argument(
        "path",
        type=str,
        help="Enter the path you would like the report to be generated to."
    )
    parser.add_argument(
        "project_id",
        type=int,
        help="Enter the Shotgun id for the project entity you want to generate a report for."
    )
    return parser


def main():
    """Added for completeness and testing, intended to be run from sg_report.py directly"""
    logger_main, logger_shot, logger_asset = utils.get_logger()
    logger = logger_shot
    parser = get_parser()
    args = parser.parse_args()

    try:
        success = asset_run(args, logger)
    except Exception as e:
        logger.exception(
            "Report generator failed with exception: \n{}".format(e)
        )
        return 1
    else:
        if not success:
            logger.info("Unable to create Asset report csv.")
        else:
            logger.info("Asset report successfully generated: \n{}".format(args.path))
        return 0


if __name__ == '__main__':
    sys.exit(main())
