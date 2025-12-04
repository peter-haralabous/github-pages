from ninja import NinjaAPI

from .form import router as form_router

api = NinjaAPI(urls_namespace="providers-api")

api.add_router("/form", form_router)
