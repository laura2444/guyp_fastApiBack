from app.models.user import User
from app.database.mongodb import connect_to_mongodb, close_mongodb, get_database
from app.schemas.user_schemas import UserRegisterSchema, UserLoginSchema, UserResponseSchema
from app.utils.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException, status
from bson import ObjectId  # importa objectId para manejar IDs de MongoDB

async def register_user(data_user: UserRegisterSchema) -> UserResponseSchema:

    try:
        db= get_database()
        collection = db["users"]

        #verifica si el usuario existe o no
        user_existing = await collection.find_one({"email": data_user.email}) #no pueden tener el mismo email
        if user_existing:
            raise HTTPException(
                status_code=400,
                detail="El usuario ya existe con este email"
            )
        #crea usuario
        user= data_user.model_dump()  # convierte el esquema a un diccionario 
        user["password"] = hash_password(user["password"])  # hashea la contraseña

        insert = await collection.insert_one(user)  # inserta el usuario en la colección

        # obtener usuario
        new_user = await collection.find_one({"_id": insert.inserted_id})  # busca el usuario recién insertado 

        if not new_user:
            raise HTTPException(
                status_code=500,
                detail="Error al crear el usuario"
            )


        token = create_access_token({"user_id": str(new_user["_id"])})

        return UserResponseSchema(
            id=str(new_user["_id"]),
            name=new_user["name"],
            email=new_user["email"],
            token=token
        )


    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Error al crear usuario", "error": str(e)}
        )

async def login_user(data_user: UserLoginSchema) -> UserResponseSchema:
    try:
        db = get_database()
        collection = db["users"]

        new_user = await collection.find_one({"email": data_user.email})
        if not new_user:
            raise HTTPException(
                status_code=404,
                detail={"message": "Correo electrónico incorrecto"}
            )
        if not verify_password(data_user.password, new_user["password"]):
            raise HTTPException(
                status_code=404,
                detail={"message": "Contraseña incorrecta"}
            )
        token = create_access_token({"user_id": str(new_user["_id"])})

        return UserResponseSchema(
            id=str(new_user["_id"]),
            name=new_user["name"],
            email=new_user["email"],
            token=token
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Error al iniciar sesión", "error": str(e)}
        )