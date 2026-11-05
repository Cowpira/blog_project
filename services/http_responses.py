from fastapi import HTTPException, status


# Success Ok -> status 200
def status_200_ok(icon: str, msg: str):
    return HTTPException(
        status_code= status.HTTP_200_OK,
        detail= [icon, msg]
    )



# Created -> status 201
def status_201_created(icon: str, msg: str):
    return HTTPException(
        status_code= status.HTTP_201_CREATED,
        detail= [icon, msg]
    )



# Accepted -> status 202
def status_202_accepted(icon: str, error_msg: str):
    return HTTPException(
        status_code= status.HTTP_202_ACCEPTED,
        detail= [icon, error_msg]
    )



# No Content -> status 204
def status_204_no_content(icon: str, error_msg: str):
    return HTTPException(
        status_code= status.HTTP_204_NO_CONTENT,
        detail= [icon, error_msg]
    )



# Moved Permanently -> status 301
def status_301_moved_permanently(icon: str, error_msg: str):
    return HTTPException(
        status_code= status.HTTP_301_MOVED_PERMANENTLY,
        detail= [icon, error_msg]
    )



# Found -> status 302
def status_302_found(icon: str, error_msg: str):
    return HTTPException(
        status_code= status.HTTP_302_FOUND,
        detail= [icon, error_msg]
    )



# Bad Request -> status 400
def status_400_bad_request(icon: str, error_msg: str):
    return HTTPException(
        status_code= status.HTTP_400_BAD_REQUEST,
        detail= [icon, error_msg]
    )



# Unauthorized -> status 401 - Not authenticated user
def status_401_unauthorized(icon: str, error_msg: str):
    return HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail= [icon, error_msg]
    )



# Forbidden -> status 403 - Authenticated but not allowed
def status_403_forbidden(icon: str, error_msg: str):
    return HTTPException(
        status_code= status.HTTP_403_FORBIDDEN,
        detail= [icon, error_msg]
    )



# Not Found -> status 404
def status_404_not_found(icon: str, error_msg: str):
    return HTTPException(
        status_code= status.HTTP_404_NOT_FOUND,
        detail= [icon, error_msg]
    )



# Not Acceptable 406
def status_406_not_acceptable(icon: str, error_msg: str):
    return HTTPException(
        status_code= status.HTTP_406_NOT_ACCEPTABLE,
        detail= [icon, error_msg]
    )



# Validation Error -> status 422 - Unprocessable Entity
def status_422_unprocessable_entity(icon: str, error_msg: str):
    return HTTPException(
        status_code= status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail= [icon, error_msg]
    )



# Validation Error -> status 422 - Unprocessable Entity
def status_429_limit_request(current_path: str):
    return HTTPException(
        status_code= status.HTTP_429_TOO_MANY_REQUESTS,
        detail= ["bi bi-flag-fill", "You have exceeded request limit", current_path]
    )



# Server Error -> status 500
def status_500_server_error(icon:str , error_msg: str):
    return HTTPException(
        status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail= [icon, error_msg]
    )



# Service Unavailable -> status 503
def status_503_service_unavailable(icon: str, error_msg: str):
    return HTTPException(
        status_code= status.HTTP_503_SERVICE_UNAVAILABLE,
        detail= [icon, error_msg]
    )