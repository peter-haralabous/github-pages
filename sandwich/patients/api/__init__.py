from ninja import NinjaAPI

from .formio import router as formio_router

api = NinjaAPI()

api.add_router("/formio", formio_router)
