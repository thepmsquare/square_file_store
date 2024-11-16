import mimetypes
import os
import uuid
from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import status, APIRouter, Form, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.params import Query
from fastapi.responses import FileResponse, JSONResponse
from square_commons import get_api_output_in_standard_format
from square_database_structure.square.file_storage.tables import File

from square_file_store.configuration import (
    global_absolute_path_local_storage,
    global_object_square_logger,
)
from square_file_store.messages import messages
from square_file_store.utils.Helper import (
    create_entry_in_file_store,
    get_file_row,
    edit_file_delete_status,
)

router = APIRouter(
    tags=["core"],
)


@router.post("/upload_file/v0", status_code=status.HTTP_201_CREATED)
@global_object_square_logger.async_auto_logger
async def upload_file_v0(
    file: UploadFile,
    app_id: Annotated[
        Optional[int],
        Form(title="App id", description="Specify the app id"),
    ] = None,
    system_relative_path: Annotated[
        str,
        Form(
            title="System relative path",
            description="Specify the path using '/'. For e.g. home/user_document",
        ),
    ] = "others/misc",
):
    try:
        """
        validation
        """
        # pass
        """
        main
        """
        file_bytes = await file.read()
        filename = file.filename
        content_type = file.content_type

        file_storage_token = str(uuid.uuid4())
        system_file_name = str(uuid.uuid4())
        file_extension = filename.rsplit(".", 1)[-1]
        system_file_name_with_extension = system_file_name + "." + file_extension
        response = create_entry_in_file_store(
            file_name_with_extension=filename,
            content_type=content_type,
            file_storage_token=file_storage_token,
            app_id=app_id,
            system_relative_path=system_relative_path,
            system_file_name_with_extension=system_file_name_with_extension,
        )

        # create folder
        system_absolute_path = os.path.join(
            global_absolute_path_local_storage,
            os.sep.join(system_relative_path.split("/")),
        )

        # create path if it doesn't exist.
        if not os.path.exists(system_absolute_path):
            os.makedirs(system_absolute_path)

        system_file_absolute_path = os.path.join(
            system_absolute_path, system_file_name_with_extension
        )
        with open(system_file_absolute_path, "wb") as file:
            file.write(file_bytes)

        # Check if the file exists
        if not os.path.exists(system_file_absolute_path):
            output_content = get_api_output_in_standard_format(
                message=messages["GENERIC_500"],
                log=f"file creation failed at {system_file_absolute_path}.",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=output_content,
            )
        """
        return value
        """
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_CREATION_SUCCESSFUL"],
            data={"main": response[0][File.file_storage_token.name]},
        )
        return JSONResponse(content=output_content, status_code=status.HTTP_201_CREATED)

    except HTTPException as http_exception:
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.get("/download_file/v0", status_code=status.HTTP_200_OK)
@global_object_square_logger.async_auto_logger
async def download_file_v0(file_storage_token: UUID):
    file_storage_token = str(file_storage_token)
    try:
        """
        validation
        """
        # pass
        """
        main
        """
        local_dict_file_row = get_file_row(file_storage_token)
        local_string_system_absolute_file_path = str(
            os.path.join(
                global_absolute_path_local_storage,
                os.sep.join(
                    local_dict_file_row[File.file_system_relative_path.name].split("/")
                ),
                local_dict_file_row[File.file_system_file_name_with_extension.name],
            )
        )

        # check file is deleted
        if local_dict_file_row[File.file_is_deleted.name]:
            output_content = get_api_output_in_standard_format(
                message=messages["GENERIC_400"],
                log=f"file: {file_storage_token} deleted.",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=output_content,
            )
        if not os.path.exists(local_string_system_absolute_file_path):
            output_content = get_api_output_in_standard_format(
                message=messages["GENERIC_500"],
                log=f"file: {file_storage_token} not found in path {local_string_system_absolute_file_path}.",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=output_content,
            )
        """
        return value
        """
        content_type, _ = mimetypes.guess_type(local_string_system_absolute_file_path)

        return FileResponse(
            local_string_system_absolute_file_path,
            media_type=content_type,
            filename=local_dict_file_row[File.file_name_with_extension.name],
        )
    except HTTPException as http_exception:
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.delete("/delete_files/v0", status_code=status.HTTP_200_OK)
@global_object_square_logger.async_auto_logger
async def delete_files_v0(file_storage_tokens: List[UUID] = Query()):
    list_file_storage_tokens = list(set(str(x) for x in file_storage_tokens))
    deleted_file_storage_tokens = []
    try:
        """
        validation
        """
        # pass
        """
        main
        """
        for file_storage_token in list_file_storage_tokens:
            # get file path
            local_dict_file_row = get_file_row(file_storage_token)
            if local_dict_file_row[File.file_is_deleted.name]:
                continue
            local_string_system_absolute_file_path = str(
                os.path.join(
                    global_absolute_path_local_storage,
                    os.sep.join(
                        local_dict_file_row[File.file_system_relative_path.name].split(
                            "/"
                        )
                    ),
                    local_dict_file_row[File.file_system_file_name_with_extension.name],
                )
            )

            # delete file
            if os.path.exists(local_string_system_absolute_file_path):
                os.remove(local_string_system_absolute_file_path)
            else:
                global_object_square_logger.logger.warning(
                    f"file {local_string_system_absolute_file_path} should have existed but doesn't."
                )

            deleted_file_storage_tokens.append(file_storage_token)
        edit_file_delete_status(deleted_file_storage_tokens)
        """
        return value
        """
        output_content = get_api_output_in_standard_format(
            data={"main": deleted_file_storage_tokens},
            message=messages["GENERIC_DELETE_SUCCESSFUL"],
        )
        return JSONResponse(content=output_content)
    except HTTPException as http_exception:
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code,
            content=http_exception.detail,
        )
    except Exception as e:
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=output_content,
        )
