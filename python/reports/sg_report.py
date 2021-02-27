import sys
import argparse

from reports import shot_report
from reports import asset_report
from reports import utils


def get_parser():
    """

    Returns: Parent module parser with subparsers for report modules

    """
    parser = argparse.ArgumentParser(
        prog="sg_report",
        description="Tool to generate a shotgun reports into the given location.",
    )

    subparsers = parser.add_subparsers(
        title="Report type",
        description="Choose which type of reports you want to generate. eg. shot, asset",
    )

    parser_shot = subparsers.add_parser(
        "shot",
        prog="shot_report",
        description="Generate a csv reports for Shotgun Shot Tasks",
        add_help=False,
        parents=[shot_report.get_parser()],
    )
    parser_shot.set_defaults(func=shot_report.shot_run)
    parser_asset = subparsers.add_parser(
        "asset",
        prog="asset_report",
        description="Generate a csv reports for Shotgun Asset Tasks",
        add_help=False,
        parents=[asset_report.get_parser()],

    )
    parser_asset.set_defaults(func=asset_report.asset_run)

    return parser


def main():
    """

    Returns: Runs report chosen in args, writes report csv to given location.

    """
    logger_main, logger_shot, logger_asset = utils.get_logger()
    parser = get_parser()
    args = parser.parse_args()

    logger_main.info("Project id: {}".format(args.project_id))
    func_name = args.func.__name__

    try:
        if "asset" in func_name:
            args.func(args, logger_asset)
        elif "shot" in func_name:
            args.func(args, logger_shot)
        else:
            args.func(args, logger_main)
    except Exception as e:
        logger_main.exception(
            "Report generator failed with exception: \n{}".format(e)
        )
        return 1
    else:
        logger_main.info("report generated to: \n{}".format(args.path))
        return 0


if __name__ == '__main__':
    sys.exit(main())
