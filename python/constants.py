class ReportConstants:
    shotgun_url = "https://studio.shotgunstudio.com"
    login = "script_name"    # Script name
    password = "script_key"  # Script key

    # Complex shotgun constants
    task_asset_status = "entity.Asset.sg_status_list"
    task_asset_name = "entity.Asset.code"
    task_asset_type = "entity.Asset.sg_asset_type"
    task_asset_shots = "entity.Asset.shots"
    task_shot_status = "entity.Shot.sg_status_list"
    task_shot_name = "entity.Shot.code"
    task_shot_seq_status = "entity.Shot.sg_sequence.Sequence.sg_status_list"
    task_shot_seq_name = "entity.Shot.sg_sequence.Sequence.code"

    # Shot task return fields
    shot_task_fields = [
        "sg_status_list",
        "step",
        "content",
        "start_date",
        "due_date",
        "entity",
        "tags",
        "est_in_mins",
        task_shot_status,
        task_shot_name,
        task_shot_seq_status,
        task_shot_seq_name,
    ]

    # Asset task return fields
    asset_task_fields = [
        "sg_status_list",
        "step",
        "content",
        "start_date",
        "due_date",
        "entity",
        "tags",
        "est_in_mins",
        "shots",
        task_asset_status,
        task_asset_name,
        task_asset_type,
        task_asset_shots,
    ]

    # Csv report headers
    asset_name = "Asset Name"
    asset_type = "Asset Type"
    due_date = "Due Date"
    id = "ID"
    prod_shot = "Production Shot"
    prod_asset = "Production Asset"
    seq_name = "Sequence Name"
    shot_name = "Shot Name"
    start_date = "Start Date"
    step = "Step"
    task_name = "Task Name"
    task_status = "Task Status"
    tags = "Tags"

    # Shot csv report header order
    shot_csv_header_order = (
        id,
        task_name,
        step,
        task_status,
        shot_name,
        prod_shot,
        seq_name,
        start_date,
        due_date,
        tags,
    )

    # Asset csv report header order
    asset_csv_header_order = (
        id,
        task_name,
        step,
        task_status,
        asset_name,
        prod_asset,
        asset_type,
        start_date,
        due_date,
        tags,
    )
