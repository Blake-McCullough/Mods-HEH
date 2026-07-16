
# import unreal

# def reimport_asset(asset_path):

#     asset = unreal.EditorAssetLibrary.load_asset(asset_path)

#     if not asset:
#         unreal.log_error(f"Could not load {asset_path}")
#         return

#     import_data = asset.get_editor_property("asset_import_data")
#     fbx_file_path = import_data.get_first_filename()

#     unreal.log(f"Reimporting from: {fbx_file_path}")

#     import_task = unreal.AssetImportTask()
#     import_task.filename = fbx_file_path
#     import_task.destination_name = asset.get_name()
#     import_task.destination_path = asset.get_path_name().rpartition("/")[0]
#     import_task.replace_existing = True
#     import_task.automated = True
#     import_task.save = True

#     asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
#     asset_tools.import_asset_tasks([import_task])

#     unreal.EditorAssetLibrary.save_asset(asset_path)

#     unreal.log("Finished reimport.")

# asset_path = "/Game/Marvel/UI/Textures/Ability/1060/icon_106011"

# reimport_asset(asset_path)

import unreal

def reimport_all(path):
    assets = unreal.EditorAssetLibrary.list_assets(path, recursive=True, include_folder=False)

    for asset_path in assets:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if not asset:
            continue
        #     asset = unreal.EditorAssetLibrary.load_asset(asset_path)

        # if not asset:
        #     unreal.log_error(f"Could not load {asset_path}")
        #     return

        import_data = asset.get_editor_property("asset_import_data")
        fbx_file_path = import_data.get_first_filename()

        unreal.log(f"Reimporting from: {fbx_file_path}")

        import_task = unreal.AssetImportTask()
        import_task.filename = fbx_file_path
        import_task.destination_name = asset.get_name()
        import_task.destination_path = asset.get_path_name().rpartition("/")[0]
        import_task.replace_existing = True
        import_task.automated = True
        import_task.save = True

        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        asset_tools.import_asset_tasks([import_task])

        unreal.EditorAssetLibrary.save_asset(asset_path)

        unreal.log("Finished reimport.")

        # import_data = asset.get_editor_property("asset_import_data")
        # fbx_file_path = import_data.get_first_filename()

        # if not fbx_file_path:
        #     continue

        # task = unreal.AssetImportTask()
        # task.filename = fbx_file_path
        # task.destination_path = asset_path.rpartition("/")[0]
        # task.destination_name = asset.get_name()
        # task.replace_existing = True

        # unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

# reimport_all("/Game/Marvel")
reimport_all("/") #reimport everything