from ninja import NinjaAPI

from .form import router as form_router
from .formio import router as formio_router

api = NinjaAPI(urls_namespace="patients-api")

api.add_router("/formio", formio_router)
api.add_router("/form", form_router)
