import argparse
import os
import sys

from reports import utils
from constants import ReportConstants


def get_shot_report_dict(all_tasks, prod_shots):
    """

    Args:
        all_tasks(list of dict): List of shotgun task entity dictionaries
        prod_shots(set): set containing production shot names.

    Returns: List of shot report dictionaries formatted for writing to csv.

    """
    # If the logic is simpler, this can be done as a list comprehension.
    csv_tasks = []
    for task in all_tasks:
        task_dict = {                                                               # Example:
            ReportConstants.id: str(task["id"]),                                    # "ID": "1234"
            ReportConstants.task_name: task["content"],                             # "Task Name": "animationBlocking"
            ReportConstants.step: task["step"].get("name", ""),                     # "Step": "animation"
            ReportConstants.task_status: task["sg_status_list"],                    # "Task Status": "ip"
            ReportConstants.shot_name: task[ReportConstants.task_shot_name],        # "Shot Name": "s0500"
            ReportConstants.seq_name: task[ReportConstants.task_shot_seq_name],     # "Sequence Name": "sq1500"
            ReportConstants.start_date: task["start_date"],                         # "Start Date:" "2021-02-25"
            ReportConstants.due_date: task["due_date"],                             # "Due Date": "2021-03-05"
            ReportConstants.prod_shot: (                                            # "Production Shot": "True"
                "True" if task[ReportConstants.task_shot_name] in prod_shots else "False"
            ),
            ReportConstants.tags: (                                                 # "Tags": "tag1, tag2, tag3"
                ", ".join(tag["name"] for tag in task["tags"])
            ),
        }
        csv_tasks.append(task_dict)
    return csv_tasks


def get_production_shots_from_tasks(all_tasks):
    """

    Args:
        all_tasks(list of dict): List shotgun task dictionaries to be filtered

    Returns: Filters down the list of given tosks to only those that match the following rules:
                    Linked shot entity is "in progress"
                    Linked shot's linked sequence entity is "in progress"

    """
    # Can add any logic here that is needed to validate production tasks.
    # prod_tasks = []
    prod_shots = []
    for task in all_tasks:
        # If linked shot is not "in progress", skip it.
        if not task[ReportConstants.task_shot_status] == "ip":
            continue
        # If linked shot's linked sequence is not "in progress", skip it.
        if not task[ReportConstants.task_shot_seq_status] == "ip":
            continue
        # Any other rules you want to add. Eg. no shots of a specific type
        # prod_tasks.append(task)
        if task[ReportConstants.task_shot_name] in prod_shots:
            continue
        prod_shots.append(task[ReportConstants.task_shot_name])

    return set(prod_shots)


def get_shot_tasks(sg, sg_project):
    """

    Args:
        sg: Shotgun_api3 Shotgun object
        sg_project(dict): Shotgun entity dictionary

    Returns: All Shotgun shot tasks linked to the given shotgun project.

    """
    filter_ = [
        ["project", "is", sg_project],
        ["entity", "type_is", "Shot"],
    ]

    return sg.find("Task", filter_, ReportConstants.shot_task_fields)


def shot_run(args, logger):
    """

    Args:
        args: parser arguments
        logger: python logging logger object

    Returns: True if csv is written to the given location.
             False if not

    """
    logger.info("Starting Shot Report generation.")

    # Getting shotgun connection and shotgun project entity
    project_id = args.project_id
    sg = utils.get_sg_connection()
    sg_project = utils.get_sg_project_from_id(sg, project_id)

    # If tool can't find a shotgun project from the given ID, exit
    if not sg_project:
        logger.warning("Could not find project from the given ID. Exiting.")
        return False

    # Getting shot tasks
    # Note, this is often the most time consuming part of the process.
    logger.info("Getting all shot tasks for project {} from Shotgun.".format(sg_project["name"]))
    shot_tasks = get_shot_tasks(sg, sg_project)
    logger.info("Got {} shot tasks.".format(len(shot_tasks)))

    # Filtering shots to a list of Production shots
    # This is so we can mark if a shot is a Production Shot or not in the final report.
    prod_shots = get_production_shots_from_tasks(shot_tasks)
    logger.debug("Got {} production shots.".format(len(prod_shots)))

    # Converting to a set of only the production shot names.
    # prod_shots = [task["entity"].get("name") for task in prod_shots]
    # prod_shots = set(prod_shots)
    # logger.debug("Got {} production shots.".format(len(prod_shots)))

    # Processing tasks into final report format.
    logger.info("Compiling report")
    report_dict = get_shot_report_dict(shot_tasks, prod_shots)

    logger.info("Writing report to csv")
    # csv will error if the path doesn't exist.
    dir_ = os.path.dirname(args.path)
    if not os.path.exists(dir_):
        logger.debug("Creating directory: \n{}".format(dir_))
        os.mkdir(dir_)

    # Writing out csv of report dictionary.
    utils.write_csv(args.path, ReportConstants.shot_csv_header_order, report_dict)
    return True


def get_parser():
    """

    Returns: Shot report module argument parser

    """
    parser = argparse.ArgumentParser(
        prog="shot_report",
        description="Generate a csv report for Shotgun Shot tasks.",
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
        success = shot_run(args, logger)
    except Exception as e:
        logger.exception(
            "Report generator failed with exception: \n{}".format(e)
        )
        return 1
    else:
        if not success:
            logger.info("Unable to create Shot report csv.")
        else:
            logger.info("Shot report successfully generated: \n{}".format(args.path))
        return 0


if __name__ == '__main__':
    sys.exit(main())
