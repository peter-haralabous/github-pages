from crispy_tailwind.templatetags.tailwind_field import CrispyTailwindFieldNode
from crispy_tailwind.templatetags.tailwind_field import CSSContainer

# monkey-patch crispy-tailwind to use daisy styles
base_input = "input w-full"

default_styles = {
    "text": base_input,
    "number": base_input,
    "radioselect": "",
    "email": base_input,
    "url": base_input,
    "password": base_input,
    "hidden": "",
    "multiplehidden": "",
    "file": "",
    "clearablefile": "",
    "textarea": base_input,
    "date": base_input,
    "datetime": base_input,
    "time": base_input,
    "checkbox": "checkbox",
    "select": "",
    "nullbooleanselect": "",
    "selectmultiple": "",
    "checkboxselectmultiple": "",
    "multi": "",
    "splitdatetime": "text-gray-700 bg-white focus:outline border border-gray-300 leading-normal px-4 appearance-none"
    " rounded-lg py-2 focus:outline-none mr-2",
    "splithiddendatetime": "",
    "selectdate": "",
    "error_border": "input-error",
}

# NOTE-NG: this is a totally gross hack
# list all the tailwind classes that crispy_tailwind uses so that they don't get stripped from our tailwind bundle.
# we should be able to @include(../../path/to/site-packages/crispy_tailwind) in our css, but we build our css before
# installing python dependencies, so that doesn't work.
# this is the output of scripts/list_crispy_tailwind_classes.sh
crispy_tailwind_classes = (
    "pointer-events-none sr-only absolute relative inset-y-0 top-0 right-0 bottom-0 mt-3 mr-2 mr-3 mb-2 mb-3 mb-4 "
    "block flex hidden h-4 h-6 w-4 w-6 w-full table-auto appearance-none flex-row items-center "
    "rounded rounded-lg rounded-t rounded-l-none rounded-r-none rounded-b "
    "border border-r-0 border-l-0 border-gray-300 border-red-400 border-red-500 "
    "bg-blue-500 bg-gray-200 bg-green-500 bg-red-100 bg-red-500 bg-white "
    "fill-current px-2 px-3 px-4 py-2 py-3 text-sm text-xs leading-normal font-bold "
    "text-gray-600 text-gray-700 text-gray-800 text-red-500 text-red-700 text-white lowercase italic filter "
    "hover:bg-blue-700 hover:bg-green-700 hover:bg-red-700 focus:outline focus:outline-none sm:inline"
)

CrispyTailwindFieldNode.default_container = CSSContainer(default_styles)
