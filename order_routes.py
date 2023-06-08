from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from models import User, Order
from schema import OrderModel, OrderStatusModel
from database import Session, engine
from fastapi.encoders import jsonable_encoder

order_router = APIRouter(
    prefix="/orders",
    tags=['orders']

)

session = Session(bind=engine)


@order_router.get("/")
async def hello(authorize: AuthJWT = Depends()):
    """
    returns hello world
    """
    try:
        authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    return {"message": "orders"}


@order_router.post("/order", status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, authorize: AuthJWT = Depends()):
    """
    ## placing an order
    this requires the following:
    - quantity : integer
    - pizza_size : str
    """
    try:
        authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    current_user = authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    new_order = Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity
    )

    new_order.user = user

    session.add(new_order)

    session.commit()

    response = {
        "pizza_size": new_order.pizza_size,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status": new_order.order_status
    }

    return jsonable_encoder(response)


@order_router.get("/orders")
async def list_all_orders(authorize: AuthJWT = Depends()):
    """
        ## listing all orders
        only accessed by superuser
    """
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    current_user = authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        orders = session.query(Order).all()

        return jsonable_encoder(orders)

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not superuser")


@order_router.get("/orders/{id}")
async def get_order_by_id(id: int, authorize: AuthJWT = Depends()):
    """
        ## get an order by its id
        this gets an order by its id only accessed by superuser
    """

    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    user = authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()

        return jsonable_encoder(order)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not allowed ")


@order_router.get("/user/orders")
async def get_user_orders(authorize: AuthJWT = Depends()):
    """
        ## get current users orders
        this lists the orders made by the currently logged-in users
    """
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    user = authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    return jsonable_encoder(current_user.order)


@order_router.get("/user/orders/{order_id}")
async def get_specific_order(order_id: int, authorize: AuthJWT = Depends()):
    """
        ## getting specific order by the currently logged-in user
        this returns an order by id for the currently logged-in user
    """
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    user = authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    orders = current_user.order

    for o in orders:
        if o.id == order_id:
            return jsonable_encoder(o)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="order doesn't exist")


@order_router.put("/order/update/{order_id}/")
async def update_order(order_id: int, order: OrderModel, authorize: AuthJWT = Depends()):
    """
        ## Updating an order
        this updates an order requires the following list:
        - quantity : integer
        - pizza_size : str
    """

    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    order_to_update = session.query(Order).filter(Order.id == order_id).first()

    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size

    session.commit()

    response = {
        "id": order_to_update.id,
        "quantity": order_to_update.quantity,
        "pizza_size": order_to_update.pizza_size,
        "order_status": order_to_update.order_status
    }

    return jsonable_encoder(response)


@order_router.patch("/order/update/{order_id}/")
async def update_order_status(order_id: int, order: OrderStatusModel, authorize: AuthJWT = Depends()):
    """
        ## Updating an order_status
        this updates an order_status requires the following list:
        - order_status : str

    """

    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    username = authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()

    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == order_id).first()
        order_to_update.order_status = order.order_status

        session.commit()

        response = {
            "id": order_to_update.id,
            "quantity": order_to_update.quantity,
            "pizza_size": order_to_update.pizza_size,
            "order_status": order_to_update.order_status
        }

        return jsonable_encoder(response)


@order_router.delete("/order/delete/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, authorize: AuthJWT = Depends()):
    """
        ## deleting an order
        this deletes an order
    """

    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    order_to_delete = session.query(Order).filter(Order.id == order_id).first()
    try:
        session.delete(order_to_delete)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="order with that id doesn't exist")
    session.commit()
    return order_to_delete

