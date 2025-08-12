import inspect

class PrivateMethod:
    """
    Descriptor to make a method private, with exceptions:
    - If method decorated with @allow_private_access
    - If caller class is in allowed_classes list
    - Or if caller module is same as owner module
    """

    allowed_classes = set()  # set nama class yang boleh akses

    def __init__(self, method):
        self.method = method
        self._is_private_method = True

    def __get__(self, instance, owner):
        if instance is None:
            return self

        frame = inspect.currentframe().f_back
        code = frame.f_code

        module_name = frame.f_globals.get("__name__")
        function_name = code.co_name
        filename = code.co_filename
        lineno = frame.f_lineno
        class_name = frame.f_locals.get("self").__class__.__name__ if "self" in frame.f_locals else None

        # Jika method di-decorate @allow_private_access
        if hasattr(self.method, "_is_allowed_on_private") and self.method._is_allowed_on_private:
            return self.method.__get__(instance, owner)

        # Cek kalau caller class di whitelist
        if class_name in self.allowed_classes:
            return self.method.__get__(instance, owner)

        # Cek kalau caller dari module yang sama
        if module_name == owner.__module__:
            return self.method.__get__(instance, owner)

        raise AttributeError(
            f"This method '{self.method.__name__}' is private and cannot be accessed from outside the class.\n"
            f"Caller Info:\n"
            f"  Module   : {module_name}\n"
            f"  Class    : {class_name or '[no class context]'}\n"
            f"  Function : {function_name}()\n"
            f"  File     : {filename}:{lineno}"
        )
