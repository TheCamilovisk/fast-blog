from fastapi import APIRouter

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/')
async def read_users():
    return {'message': 'List of users'}


@router.get('/{user_id}')
async def read_user(user_id: int):
    return {'message': 'User details', 'user_id': user_id}


@router.post('/')
async def create_user(user: dict):
    return {'message': 'User created', 'user': {'id': 1} | user}


@router.put('/{user_id}')
async def update_user(user_id: int, user: dict):
    return {'message': 'User updated', 'user_id': user_id, 'user': user}


@router.delete('/{user_id}')
async def delete_user(user_id: int):
    return {'message': 'User deleted', 'user_id': user_id}
